"""CLI: offline evidence packet or explicitly consented external visual intake."""
import argparse
import json
from pathlib import Path
from engine import load_packet, run
from vision_adapter import ingest_photos


def main():
    p=argparse.ArgumentParser(description='MOTIF-FIELD-004, experimental autonomous reframe')
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--packet', type=Path)
    group.add_argument('--photos',nargs='+')
    p.add_argument('--goal',help='Describe what you want to achieve; required with --photos')
    p.add_argument('--model',help='Explicit model name for optional photo analysis')
    p.add_argument('--consent-send-images', action='store_true',
                   help='Opt in to sending supplied photos to the external model API')
    args=p.parse_args()
    if args.packet:
        inp=load_packet(json.loads(args.packet.read_text()))
    else:
        if not args.goal or not args.model:
            p.error('--photos requires --goal and --model')
        inp=ingest_photos(args.photos,args.goal,model=args.model,
                          allow_external=args.consent_send_images)
    print(json.dumps(run(inp),indent=2))


if __name__=='__main__':
    main()
