"""Run offline; primary-only supports the initial benchmark freeze."""
import argparse
from src.pipeline import generate_primary, generate_benchmark_report
from src.report import generate_report, generate_notebook

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary-only',action='store_true')
    args=parser.parse_args()
    result=generate_primary()
    if not args.primary_only:generate_benchmark_report()
    generate_report();generate_notebook()
    print(result)

if __name__=='__main__':main()
