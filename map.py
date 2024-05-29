from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus
import xmltodict, json
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import TagFilterButton
from st_pages import Page, show_pages

# 데이터 불러오기(github + OpenAPI)
table = pd.read_html("https://inasie.github.io/%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D/5/", encoding = "utf-8")[0]
table["code"] = table["법정동코드"].apply(lambda x:str(x)[:2] )
table2 = table.drop_duplicates("code", keep = "first")

key = "개인 API 인증키"
final_data = []

for a, b,c in table2.itertuples(index = False):
    url = f"http://apis.data.go.kr/B552584/EvCharger/getChargerInfo?serviceKey={key}&"
    queryParams = urlencode({quote_plus("numOfRows"):"9999", quote_plus("pageNo"):"1", quote_plus("zcode"):c})
    url2 = url + queryParams
    response = urlopen(url2) 
    results = response.read().decode("utf-8")
    results_to_json = xmltodict.parse(results)
    data = json.loads(json.dumps(results_to_json))
    final_data.extend(data["response"]["body"]["items"]["item"])

df = pd.DataFrame(final_data)
df.rename(columns = {"statNm":"stationName", "addr":"address", "useTime":"useHour", "lat":"latitude",
                     "lng":"longitude", "busiCall":"telNum", "parkingFree":"fee"}, inplace = True)

# 필요없는 columns 제거, address기준으로 중복 rows 제거
df = df[["stationName", "address", "latitude", "longitude", "useHour", "telNum", "fee"]].drop_duplicates(subset = ["address"])

# # DB에 보내기
# db_connection_str = "mysql+pymysql://root@192.168.0.30:3306/cardb"
# db_connection = create_engine(db_connection_str)
# db_conn = db_connection.connect()
# df_drop.to_sql(name = "map", con = db_connection, schema = "cardb", if_exists = "replace", index = False)

# # DB에서 데이터 가져오기
# @st.cache_data()
# def load_data():
#     db_connection_str = "mysql+pymysql://root@192.168.0.30:3306/cardb"
#     db_connection = create_engine(db_connection_str)
#     db_conn = db_connection.connect()
#     df = pd.read_sql_query("SELECT * FROM map", db_conn)
#     return df
# df = load_data()

admin_dist = ["서울특별시", "부산광역시", "인천광역시",
              "대구광역시", "대전광역시", "광주광역시",
              "울산광역시", "경상북도", "세종특별자치시", "경기도", 
              "충청북도", "충청남도", "전라남도", "경상남도",
              "강원특별자치도", "전북특별자치도", "제주특별자치도"]

# 마커가 여러개인 지도 만드는 함수
@st.cache_data(experimental_allow_widgets=True)
def mk_map(dataframe, start_lat, start_lon):

    # 마커 만드는 함수
    def get_marker(lat, lon, parking, info):
        colors = {"N":"#FF6F61", "Y":"#1E90FF"}
        return folium.CircleMarker(location=[lat, lon], radius=5, fill_opacity=0.8, 
                                    fill_color=colors[parking], color=colors[parking], 
                                    weight=1, tooltip=info, tags=[parking])
    
    map = folium.Map(location=[start_lat, start_lon], 
                        tiles="CartoDB positron", zoom_start=11)

    for parking in dataframe["fee"].unique():
        temp = dataframe[dataframe["fee"] == parking]
        for i in temp.index:
            if parking == "N":
                info = f"""
                    <font size=2.5> {temp["stationName"][i]} </font><br>
                    <font size=2.2> 주소: {temp["address"][i]} </font><br>
                    <font size=1.6> 이용시간: {temp["useHour"][i]} </font><br>
                    <font size=1.6> 전화번호: {temp["telNum"][i]} </font><br>
                    <font size=1.6> 주차료: {parking}O </font>
                    """
            else:
                info = f"""
                    <font size=2.5> {temp["stationName"][i]} </font><br>
                    <font size=2.2> 주소: {temp["address"][i]} </font><br>
                    <font size=1.6> 이용시간: {temp["useHour"][i]} </font><br>
                    <font size=1.6> 전화번호: {temp["telNum"][i]} </font><br>
                    <font size=1.6> 주차료: {parking}ES </font>
                    """
            get_marker(temp["latitude"][i], temp["longitude"][i], parking, info).add_to(map)

    TagFilterButton(dataframe["fee"].unique().tolist()).add_to(map)
    folium.Circle([start_lat, start_lon], color = "tomato", radius=10*1000).add_to(map)
    st_folium(map, width=700, height = 550)

# 마커가 1개일 때 지도 만드는 함수
def mk_map_one(dataframe, value):
    temp = dataframe[dataframe["stationName"] == value]
    if temp.empty:
        return
    parking = temp["fee"].iloc[0]
    loc_lat = temp["latitude"].iloc[0]
    loc_lon = temp["longitude"].iloc[0]
    
    def get_marker(lat, lon, info):
        colors = {"N":"#FF6F61", "Y":"#1E90FF"}
        return folium.CircleMarker(location=[lat, lon], radius=5, fill_opacity=0.8, 
                                    fill_color=colors[parking], color=colors[parking], 
                                    weight=1, tooltip=info, tags=[parking])

    map = folium.Map(location=[loc_lat, loc_lon], 
                        tiles="CartoDB positron", zoom_start=11)

    if parking == "N":
        info = f"""
            <font size=2.5> {value} </font><br>
            <font size=2.2> 주소: {temp["address"].values[0]} </font><br>
            <font size=1.6> 이용시간: {temp["useHour"].values[0]} </font><br>
            <font size=1.6> 전화번호: {temp["telNum"].values[0]} </font><br>
            <font size=1.6> 주차료: NO </font>
            """
    else:
        info = f"""
            <font size=2.5> {value} </font><br>
            <font size=2.2> 주소: {temp["address"].values[0]} </font><br>
            <font size=1.6> 이용시간: {temp["useHour"].values[0]} </font><br>
            <font size=1.6> 전화번호: {temp["telNum"].values[0]} </font><br>
            <font size=1.6> 주차료: YES </font>
            """
        get_marker(loc_lat, loc_lon, info).add_to(map)

    TagFilterButton(dataframe["fee"].unique().tolist()).add_to(map)
    folium.Circle([start_lat, start_lon], color="tomato", radius=10*1000).add_to(map)
    st_folium(map, width=700, height = 550)

# page 생성
show_pages([Page("video.py", "Video", "📼"),
            Page("map.py", "Map", "🗺️"),
            Page("layout.py", "FAQ", "❓")])

# sidebar
with st.sidebar:
    # 검색했을 때
    search = st.text_input("충전소 검색")
    if search:
        df_search = df[df["stationName"].str.contains(search)]
        if len(df_search) == 0:
            st.markdown(":red[다른 충전소를 검색해주세요]")
        else:
            df_search.reset_index(inplace = True)
            button = st.button("📜", help = "검색한 충전소 목록")
            if button:
                st.dataframe(df_search["stationName"])

    select_region = st.selectbox("지역", ["선택", "전국"] + admin_dist)

    # 전국을 선택했을 때(전체 데이터)
    if select_region == "전국":
        select_all = st.selectbox("선택", ["선택"] + df["stationName"].tolist())
        button = st.button("📜", help = f"{select_region} 충전소 목록")
        if button:
            st.dataframe(df["stationName"])

    # 특정 지역을 선택했을 때
    for i in admin_dist:
        if select_region == i:
            temp = df[df["address"].str.contains(i)]
            temp.reset_index(inplace = True)
            select_part = st.selectbox("선택", ["선택"] + temp["stationName"].tolist())
            button = st.button("📜", help = f"{select_region} 충전소 목록")
            if button:
                st.dataframe(temp["stationName"])

# 검색어 입력시 검색어가 포함된 충전소의 위치 지도
if search:
    select_region, select_all, select_part = "선택", "선택", "선택"  # 검색을 했을 땐 검색한 충전소의 지도만 나오게 하기 위해
    if len(df_search) == 0:
        st.markdown(":red[검색 결과가 없습니다.]")
    else:
        st.markdown(f"### :blue-background[검색어: {search}]")
        start_lat, start_lon = df_search["latitude"][0], df_search["longitude"][0]
        mk_map(df_search, start_lat, start_lon)

# 전국 선택했을 때 지도
if select_region == "전국":
    start_lat, start_lon = 37.466613, 126.889249  # 독산역 좌표
    if select_all and select_all != "선택":
        st.markdown(f"### :blue-background[select_all]")
        mk_map_one(df, select_all) 
    st.markdown(f"### :blue-background[지역: {select_region}]")
    mk_map(df, start_lat, start_lon)

# 특정 지역 선택했을 때 지도
for i in admin_dist:
    if select_region == i: 
        temp = df[df["address"].str.contains(i)]
        temp.reset_index(inplace = True)
        start_lat, start_lon = temp["latitude"][0], temp["longitude"][0]
        if select_part and select_part != "선택":
            st.markdown(f"### :blue-background[{select_part}]")
            mk_map_one(temp, select_part)
        st.markdown(f"### :blue-background[지역: {select_region}]")
        mk_map(temp, start_lat, start_lon)