import pandas as pd
from pathlib import Path

# 현재 파이썬 파일이 있는 폴더
folder = Path(__file__).parent

# 2017~2025 엑셀 파일 찾기
files = sorted(folder.glob("*.xlsx"))

print(f"찾은 파일: {len(files)}개")

all_data = []

for file in files:
    print(f"읽는 중: {file.name}")

    # 엑셀 읽기
    df = pd.read_excel(file)

    # 어느 연도 파일인지 기록
    year = file.name

    df["연도"] = year

    all_data.append(df)

# 모든 데이터 합치기
merged = pd.concat(all_data, ignore_index=True)

# 하나의 엑셀 파일로 저장
output = folder / "항공통계_2017_2025_통합.xlsx"
merged.to_excel(output, index=False)

print()
print("================================")
print("통합 완료!")
print(f"저장 위치: {output}")
print(f"전체 행 수: {len(merged):,}")
print(f"전체 열 수: {len(merged.columns)}")
print("================================")
