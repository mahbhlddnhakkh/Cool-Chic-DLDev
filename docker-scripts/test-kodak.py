# https://orange-opensource.github.io/Cool-Chic/results/image/compression_performance.html
# results/v4.2/image-kodak.tsv

import os
import subprocess
import glob
import shutil

import numpy as np

TOOLBOX_PATH = f"{os.path.dirname(__file__)}/../toolbox/toolbox/"
COOL_CHIC_PATH = f"{os.path.dirname(__file__)}/../coolchic"
SAMPLE_PATH = f"{os.path.dirname(__file__)}/../samples"

def verify_test_subjects(test_lambdas: list[int], test_subjects: list[dict]):
    test_lambdas_len = len(test_lambdas)
    for subject in test_subjects:
        assert(len(subject.get("psnr-results")) == test_lambdas_len)
        assert(len(subject.get("bitrate-results")) == test_lambdas_len)

def encode(subject_path: str, bitstream_path: str, workdir: str, lmbda: float):
    subprocess.call(f"mkdir -p {workdir}", shell=True)
    subprocess.call(f"rm -f {workdir}*-frame_encoder.pt", shell=True)
    cmd = (
        f"python3 {SAMPLE_PATH}/encode.py "
        f'--input={subject_path} '
        f'--output={bitstream_path} '
        f'--workdir={workdir} '
        f'--lmbda={lmbda} '
    )
    subprocess.call(cmd, shell=True)

def decode(bitstream_path: str, decoded_path: str):
    cmd = (
        f'python3 {COOL_CHIC_PATH}/decode.py '
        f'--input={bitstream_path} '
        f'--output={decoded_path} '
        '--verbosity=2 '
    )
    subprocess.call(cmd, shell=True)

def parse_encoder_log(results_log_path: str) -> dict[str, any]:
    res = {}
    encoder_logs = [x.rstrip("\n") for x in open(results_log_path).readlines()]
    keys = [x for x in encoder_logs[0].split(' ') if x]
    vals = [x for x in encoder_logs[1].split(' ') if x]
    encoder_results = {k: v for k, v in zip(keys, vals)}
    res["rate_bpp"] = float(encoder_results.get("rate_bpp"))
    res["mse"] = 10 ** (-float(encoder_results.get("psnr_db")) / 10)
    res["psnr_db"] = -10 * np.log10(res["mse"] + 1e-10)
    return res

def evaluate_decoder_side(subject_path: str, bitstream_path: str, decoded_path: str) -> dict[str, any]:
    # ---- Get rate
    cmd = (
        f"python3 {TOOLBOX_PATH}/identify.py "
        f"--input={decoded_path} "
        f"--noheader "
    )
    out_identify = subprocess.getoutput(cmd)

    width, height, n_frames = [int(x) for x in out_identify.split()[:3] if x]
    n_pixels = width * height * n_frames

    rate_bytes = os.path.getsize(bitstream_path)
    rate_bpp = rate_bytes * 8 / n_pixels

    decoder_results = {
        "n_frames": n_frames,
        "width": width,
        "height": height,
        "rate_bpp": rate_bpp
    }
    assert(n_frames == 1)
    # ---- Get PSNR
    cmd = (
        f"python3 {TOOLBOX_PATH}/quality_psnr.py "
        f"--candidate={decoded_path} "
        f"--ref={subject_path} "
        f"--noheader "
        f"--verbosity=1"
    )
    out = subprocess.getoutput(cmd)

    psnr_db_rgb = float([x for x in out.split() if x][1])
    decoder_results.update({"psnr_db": float(psnr_db_rgb)})
    return decoder_results

if __name__ == "__main__":
    test_lambdas = [0.0001, 0.0004, 0.001, 0.004, 0.02]
    # 'psnr-results-actual': [40.3548, 35.4949, 32.2333, 27.9299, 24.428]
    # 'bitrate-results-actual': [2.1490885416666665, 1.2933756510416667, 0.8358561197916666, 0.3350830078125, 0.094970703125]
    test_subjects = [
        {
            "filename": "kodim01.png",
            "psnr-results": [40.3548, 35.4949, 32.2333, 27.9299, 24.428],
            "bitrate-results": [2.1490885416666665, 1.2933756510416667, 0.8358561197916666, 0.3350830078125, 0.094970703125],
            "psnr-results-actual": [None]*len(test_lambdas),
            "bitrate-results-actual": [None]*len(test_lambdas)
        }
    ]
    verify_test_subjects(test_lambdas, test_subjects)
    # use abs path
    for subject in test_subjects:
        subject["path"] = os.path.join(os.path.dirname(__file__), "..", "dataset-test", subject.get("filename"))
    test_workdir = os.path.join(os.path.dirname(__file__), "..", "dataset-tests-res")
    subprocess.call(f"rm -f {test_workdir}/*/*", shell=True)
    subprocess.call(f"rmdir {test_workdir}/*", shell=True)
    for subject in test_subjects:
        test_workdir_tmp = os.path.join(test_workdir, subject.get('filename'))
        os.makedirs(test_workdir_tmp, exist_ok=True)
        shutil.copyfile(subject.get("path"), os.path.join(test_workdir_tmp, subject.get('filename')))
        for lmbda_i, lmbda in enumerate(test_lambdas):
            print(subject.get('filename'), lmbda)
            test_workdir_tmp = os.path.join(test_workdir, subject.get('filename'), str(lmbda))
            os.makedirs(test_workdir_tmp, exist_ok=True)
            subprocess.call(f"rm -f {test_workdir_tmp}/*", shell=True)
            subject_path = subject.get("path")
            subject_name = subject.get('filename')
            decoded_path = f"{test_workdir_tmp}/{subject_name}.ppm"
            bitstream_path = f'{test_workdir_tmp}/{subject_name}.cool'

            encode(subject_path, bitstream_path, test_workdir_tmp, lmbda)
            decode(bitstream_path, decoded_path)

            enc_res = parse_encoder_log(
                glob.glob(f"{test_workdir_tmp}/*-results_best.tsv")[0]
            )
            dec_res = evaluate_decoder_side(subject_path, bitstream_path, decoded_path)

            enc_psnr_db = enc_res['psnr_db']
            dec_psnr_db = dec_res['psnr_db']
            enc_rate_bpp = enc_res['rate_bpp']
            dec_rate_bpp = dec_res['rate_bpp']

            subject["psnr-results-actual"][lmbda_i] = dec_psnr_db
            subject["bitrate-results-actual"][lmbda_i] = dec_rate_bpp

            # Sanity checks
            delta_psnr = enc_psnr_db - dec_psnr_db
            threshold_delta_psnr = 0.3
            assert abs(delta_psnr) < threshold_delta_psnr, (
                f"Difference between the estimated PSNR at the encoder side "
                f"({enc_psnr_db:5.3f} dB) and the actual PSNR "
                f"({dec_psnr_db:5.3f} dB) is greater than the expected threshold: "
                f"+/- {threshold_delta_psnr:.2f} dB."
            )
            threshold_ratio_rate = 0.2
            ratio_rate = (dec_rate_bpp - enc_rate_bpp) / enc_rate_bpp
            assert abs(ratio_rate) < threshold_ratio_rate, (
                f"Difference between the estimated rate at the encoder side "
                f"({enc_rate_bpp:5.3f} bpp) and the actual rate "
                f"({dec_rate_bpp:5.3f} bpp) is greater than the expected threshold: "
                f"+/- {100 * ratio_rate:.2f} %."
            )
            # continue

            delta_test_psnr = subject["psnr-results"][lmbda_i] - dec_psnr_db
            threshold_delta_test_psnr = 1.5
            assert abs(delta_test_psnr) <= threshold_delta_test_psnr, (
                f"Difference between the tested PSNR "
                f"({subject['psnr-results'][lmbda_i]:5.3f} dB) and the actual PSNR "
                f"({dec_psnr_db}) dB is greater than expected threshold: "
                f"+/- {threshold_delta_test_psnr:.2f} dB."
            )
            delta_test_bitrate = subject["bitrate-results"][lmbda_i] - dec_rate_bpp
            threshold_delta_test_bitrate = 0.15
            assert abs(delta_test_bitrate) <= threshold_delta_test_bitrate, (
                f"Difference between the tested rate "
                f"({subject['bitrate-results'][lmbda_i]:5.3f} bpp) and the actual rate "
                f"({dec_rate_bpp:5.3f} bpp) is greater than the expected threshold: "
                f"+/- {100 * threshold_delta_test_bitrate:.2f} %."
            )
    print(test_subjects)
    print("TESTS DONE!")
