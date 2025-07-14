import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium

import sys
sys.stdout.reconfigure(encoding='utf-8')


#한글 폰트
import matplotlib
matplotlib.rc('font', family='Malgun Gothic')  # 윈도우용


# ---------- STEP 1: 데이터 로드 ----------
print("📥 business.json 로딩 중...")
business = pd.read_json("data/business.json", lines=True)

print("📥 review.json 로딩 중 (chunk 처리)...")
reviews_iter = pd.read_json("data/review.json", lines=True, chunksize=500000)
reviews = pd.concat(reviews_iter)

# ---------- STEP 2: Canada 맛집 필터링 ----------
# 캐나다 주 목록 (AB = Alberta, BC = British Columbia, ON = Ontario 등)
canada_states = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']
mask_state = business['state'].isin(canada_states)
mask_category = business['categories'].str.contains('Restaurants', na=False)

canada_restaurants = business[mask_state & mask_category]
print(f"🍁 Canada 맛집 개수: {len(canada_restaurants)}")

# ---------- STEP 3: Canada 리뷰 필터링 ----------
canada_business_ids = canada_restaurants['business_id'].tolist()
canada_reviews = reviews[reviews['business_id'].isin(canada_business_ids)]
print(f"📝 Canada 리뷰 개수: {len(canada_reviews)}")

# ---------- STEP 4: 결과 저장 ----------
canada_restaurants.to_csv("data/canada_restaurants.csv", index=False)
canada_reviews.to_csv("data/canada_reviews.csv", index=False)
print("✅ Canada 맛집 및 리뷰 데이터 저장 완료")

# ---------- STEP 5: Top 10 맛집 출력 ----------
top10 = canada_restaurants.sort_values(
    ['stars', 'review_count'], ascending=False).head(100)
print("\n🏆 Canada Top 100 맛집:")
print(top10[['name', 'city', 'stars', 'review_count']])

# ---------- STEP 6: 별점 분포 시각화 ----------
plt.figure(figsize=(8, 6))
sns.histplot(canada_restaurants['stars'], bins=10, kde=True, color="green")
plt.title('Canada 맛집 별점 분포')
plt.xlabel('별점')
plt.ylabel('맛집 수')
plt.savefig("data/canada_rating_distribution.png")
plt.show()
print("📊 별점 분포 그래프 저장 완료: data/canada_rating_distribution.png")

# ---------- STEP 7: 지도 시각화 ----------
canada_map = folium.Map(location=[56.1304, -106.3468], zoom_start=4)  # 캐나다 중심 좌표

for _, row in top10.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['name']} ({row['stars']}⭐, {row['review_count']} reviews)",
        icon=folium.Icon(color="red", icon="cutlery", prefix='fa')
    ).add_to(canada_map)

canada_map.save("data/canada_top10_map.html")
print("🗺️ Top10 맛집 지도 저장 완료: data/canada_top10_map.html")
