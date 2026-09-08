import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. 기본 설정
# ============================================================

folder = Path(__file__).parent
input_file = folder / "항공통계_2017_2025_통합.xlsx"

# 결과 폴더
result_folder = folder / "results"
result_folder.mkdir(exist_ok=True)


# ============================================================
# 2. 데이터 불러오기
# ============================================================

df = pd.read_excel(input_file)


# ============================================================
# 3. 전체 합계 데이터만 사용
# ============================================================

df = df[df["항공사명"] == "전체 합계"].copy()


# ============================================================
# 4. 날짜 변환
# ============================================================

df["날짜"] = pd.to_datetime(
    df["년월"]
    .astype(str)
    .str.replace("년", "-", regex=False)
    .str.replace("월", "", regex=False)
    .str.replace(" ", "", regex=False),
    format="%Y-%m"
)


# ============================================================
# 5. 여객 수 숫자형 변환
# ============================================================

df["여객(명)"] = pd.to_numeric(
    df["여객(명)"],
    errors="coerce"
)


# ============================================================
# 6. 날짜순 정렬
# ============================================================

df = df.sort_values("날짜").reset_index(drop=True)


# ============================================================
# 7. 연도 / 월 컬럼 생성
# ============================================================

df["연도_num"] = df["날짜"].dt.year
df["월"] = df["날짜"].dt.month


# ============================================================
# 8. 기본 데이터 확인
# ============================================================

print()
print("=" * 70)
print("2017~2025 항공 여객 시계열 분석")
print("=" * 70)

print()
print("[1. 데이터 기본 정보]")
print(f"데이터 개수 : {len(df):,}개월")
print(f"시작 날짜   : {df['날짜'].min().date()}")
print(f"종료 날짜   : {df['날짜'].max().date()}")

print()
print("[2. 결측치 확인]")
print(df[["날짜", "여객(명)"]].isnull().sum())


# ============================================================
# 9. 연도별 통계
# ============================================================

yearly = (
    df.groupby("연도_num")["여객(명)"]
    .agg(
        총여객수="sum",
        월평균="mean",
        최대월="max",
        최소월="min"
    )
    .reset_index()
)

yearly["전년대비증감률(%)"] = (
    yearly["총여객수"]
    .pct_change()
    * 100
)

print()
print("=" * 70)
print("[3. 연도별 항공 여객 분석]")
print("=" * 70)

print(
    yearly.to_string(
        index=False,
        formatters={
            "총여객수": "{:,.0f}".format,
            "월평균": "{:,.0f}".format,
            "최대월": "{:,.0f}".format,
            "최소월": "{:,.0f}".format,
            "전년대비증감률(%)": (
                lambda x:
                "-" if pd.isna(x)
                else f"{x:.2f}"
            )
        }
    )
)


# ============================================================
# 10. 연도별 분석 결과 저장
# ============================================================

yearly.to_excel(
    result_folder / "연도별_항공여객_분석.xlsx",
    index=False
)


# ============================================================
# 11. 코로나 전후 분석
# ============================================================

passenger_2019 = yearly.loc[
    yearly["연도_num"] == 2019,
    "총여객수"
].iloc[0]

passenger_2020 = yearly.loc[
    yearly["연도_num"] == 2020,
    "총여객수"
].iloc[0]

passenger_2022 = yearly.loc[
    yearly["연도_num"] == 2022,
    "총여객수"
].iloc[0]

passenger_2023 = yearly.loc[
    yearly["연도_num"] == 2023,
    "총여객수"
].iloc[0]

passenger_2024 = yearly.loc[
    yearly["연도_num"] == 2024,
    "총여객수"
].iloc[0]

passenger_2025 = yearly.loc[
    yearly["연도_num"] == 2025,
    "총여객수"
].iloc[0]


covid_change = (
    (passenger_2020 - passenger_2019)
    / passenger_2019
    * 100
)

recovery_2023 = (
    passenger_2023
    / passenger_2019
    * 100
)

recovery_2024 = (
    passenger_2024
    / passenger_2019
    * 100
)

recovery_2025 = (
    passenger_2025
    / passenger_2019
    * 100
)


print()
print("=" * 70)
print("[4. 코로나19 전후 분석]")
print("=" * 70)

print(f"2019년 총 여객 수 : {passenger_2019:,.0f}명")
print(f"2020년 총 여객 수 : {passenger_2020:,.0f}명")
print(f"2019→2020 변화율  : {covid_change:.2f}%")

print()
print("[코로나 이전 2019년 대비 회복률]")
print(f"2023년 : {recovery_2023:.2f}%")
print(f"2024년 : {recovery_2024:.2f}%")
print(f"2025년 : {recovery_2025:.2f}%")


# ============================================================
# 12. 가장 많은 연도 / 가장 적은 연도
# ============================================================

max_year_row = yearly.loc[
    yearly["총여객수"].idxmax()
]

min_year_row = yearly.loc[
    yearly["총여객수"].idxmin()
]

print()
print("=" * 70)
print("[5. 연도별 최고 / 최저]")
print("=" * 70)

print(
    f"가장 많은 연도 : "
    f"{int(max_year_row['연도_num'])}년 "
    f"({max_year_row['총여객수']:,.0f}명)"
)

print(
    f"가장 적은 연도 : "
    f"{int(min_year_row['연도_num'])}년 "
    f"({min_year_row['총여객수']:,.0f}명)"
)


# ============================================================
# 13. 월별 계절성 분석
# ============================================================

monthly_avg = (
    df.groupby("월")["여객(명)"]
    .mean()
    .reset_index()
)

max_month_row = monthly_avg.loc[
    monthly_avg["여객(명)"].idxmax()
]

min_month_row = monthly_avg.loc[
    monthly_avg["여객(명)"].idxmin()
]

print()
print("=" * 70)
print("[6. 월별 계절성 분석]")
print("=" * 70)

print(
    f"평균 여객 수가 가장 많은 달 : "
    f"{int(max_month_row['월'])}월 "
    f"({max_month_row['여객(명)']:,.0f}명)"
)

print(
    f"평균 여객 수가 가장 적은 달 : "
    f"{int(min_month_row['월'])}월 "
    f"({min_month_row['여객(명)']:,.0f}명)"
)


# ============================================================
# 14. 월별 계절성 결과 저장
# ============================================================

monthly_avg.to_excel(
    result_folder / "월별_계절성_분석.xlsx",
    index=False
)


# ============================================================
# 15. 그래프 1
# 전체 기간 월별 항공 여객 추이
# ============================================================

plt.figure(figsize=(15, 6))

plt.plot(
    df["날짜"],
    df["여객(명)"],
    linewidth=1.5
)

plt.title("2017-2025 Monthly Air Passenger Trend")
plt.xlabel("Date")
plt.ylabel("Passengers")

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    result_folder / "01_월별_항공여객_추이.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 16. 그래프 2
# 연도별 총 여객 수
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    yearly["연도_num"],
    yearly["총여객수"],
    marker="o",
    linewidth=2
)

plt.title("Annual Air Passenger Volume")
plt.xlabel("Year")
plt.ylabel("Passengers")

plt.xticks(yearly["연도_num"])

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    result_folder / "02_연도별_항공여객.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 17. 그래프 3
# 코로나 전후 비교
# ============================================================

comparison = yearly[
    yearly["연도_num"].isin(
        [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    )
]

plt.figure(figsize=(12, 6))

plt.plot(
    comparison["연도_num"],
    comparison["총여객수"],
    marker="o",
    linewidth=2
)

plt.axvline(
    x=2020,
    linestyle="--",
    linewidth=1
)

plt.title("COVID-19 Impact and Recovery of Air Passengers")
plt.xlabel("Year")
plt.ylabel("Passengers")

plt.xticks(comparison["연도_num"])

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    result_folder / "03_코로나_전후_항공여객.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 18. 그래프 4
# 월별 평균 계절성
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_avg["월"],
    monthly_avg["여객(명)"],
    marker="o",
    linewidth=2
)

plt.title("Monthly Seasonality of Air Passenger Volume")
plt.xlabel("Month")
plt.ylabel("Average Passengers")

plt.xticks(range(1, 13))

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    result_folder / "04_월별_계절성.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 19. 분석 결과 CSV 저장
# ============================================================

df.to_excel(
    result_folder / "정제된_항공여객_시계열.xlsx",
    index=False
)


# ============================================================
# 20. 최종 완료 메시지
# ============================================================

print()
print("=" * 70)
print("모든 분석이 완료되었습니다.")
print("=" * 70)

print()
print("생성된 결과 파일:")

for file in sorted(result_folder.iterdir()):
    print(f" - {file.name}")

print()
print(f"결과 폴더: {result_folder}")
print("=" * 70)
