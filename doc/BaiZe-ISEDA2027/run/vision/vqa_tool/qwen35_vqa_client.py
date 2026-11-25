#!/usr/bin/env python3
"""Thin CLI client for the Qwen3.5-2B VQA server.

cline / designflow call this as a tool:
    python qwen35_vqa_client.py --image /path/to/wave.png --question "How many cycles?"
prints the model's answer to stdout (plain text). Exit 0 on success, non-zero
on error. Use --json for a full JSON line (answer + elapsed_s).
"""
import argparse, json, sys, urllib.request


def vqa(server, image_path=None, image_b64=None, question="",
        max_new_tokens=512, temperature=0.0, timeout=120):
    body = {"question": question, "max_new_tokens": max_new_tokens,
            "temperature": temperature}
    if image_path:
        body["image_path"] = image_path
    elif image_b64:
        body["image_b64"] = image_b64
    req = urllib.request.Request(server.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os_env())
    ap.add_argument("--image", help="path to image file (shared NFS)")
    ap.add_argument("--image-b64", help="base64 image (alternative to --image)")
    ap.add_argument("--question", "-q", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=512)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--json", action="store_true", help="print full JSON line")
    args = ap.parse_args()
    try:
        res = vqa(args.server, args.image, args.image_b64, args.question,
                  args.max_new_tokens, args.temperature, args.timeout)
    except Exception as e:
        print(f"VQA ERROR: {e}", file=sys.stderr); sys.exit(2)
    if not res.get("ok"):
        print(f"VQA ERROR: {res.get('error')}", file=sys.stderr); sys.exit(1)
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(res.get("answer", ""))


def os_env():
    import os
    return os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")


if __name__ == "__main__":
    main()
