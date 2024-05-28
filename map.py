import streamlit as st
from bs4 import BeautifulSoup
import requests
import pandas as pd
from urllib.request import urlopen
import xmltodict
import json
from urllib.parse import urlencode, unquote, quote_plus
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, TagFilterButton
import random
import numpy as np
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy import text
import sqlalchemy
from st_pages import Page, show_pages, add_page_title

# # DB에서 데이터 가져오기

@st.cache_data()
def load_data():
    db_connection_str = 'mysql+pymysql://root@192.168.0.30:3306/cardb'
    db_connection = create_engine(db_connection_str)
    db_conn = db_connection.connect()
    df = pd.read_sql_query("SELECT * FROM map", db_conn)
    return df
df = load_data()

admin_dist = ['서울특별시', '부산광역시', '인천광역시',
              '대구광역시', '대전광역시', '광주광역시',
              '울산광역시', '경상북도', '세종특별자치시', '경기도', 
              '충청북도', '충청남도', '전라남도', '경상남도',
              '강원특별자치도', '전북특별자치도', '제주특별자치도']


@st.cache_data(experimental_allow_widgets=True)
def mk_map(dataframe, start_lat, start_lon):
    def get_marker(lat, lon, parking, info):
        colors = {"N":"#FF6F61", "Y":"#1E90FF"}
        return folium.CircleMarker(location=[lat, lon],
                                    radius=5, 
                                    fill_opacity=0.8, 
                                    fill_color=colors[parking],  
                                    color=colors[parking], 
                                    weight=1, 
                                    tooltip=info,
                                    tags=[parking]
                                    )

    map = folium.Map(location=[start_lat, start_lon], 
                        tiles="CartoDB positron", zoom_start=11)

    for parking in dataframe["fee"].unique():
        temp = dataframe[dataframe["fee"] == parking]
        for i in temp.index:
            try:
                if parking == "N":
                    info = f"""
                        <font size=2.5>{temp["stationName"][i]} </font> <br>
                        <font size=2.2>주소: {temp["address"][i]} </font> <br>
                        <font size=1.6>이용시간: {temp['useHour'][i]} </font> <br>
                        <font size=1.6>전화번호: {temp['telNum'][i]} </font> <br>
                        <font size=1.6>주차료: {parking}O </font>
                        """
                else:
                    info = f"""
                        <font size=2.5>{temp["stationName"][i]} </font> <br>
                        <font size=2.2>주소: {temp["address"][i]} </font> <br>
                        <font size=1.6>이용시간: {temp['useHour'][i]} </font> <br>
                        <font size=1.6>전화번호: {temp['telNum'][i]} </font> <br>
                        <font size=1.6>주차료: {parking}ES </font>
                        """
                get_marker(temp["latitude"][i], temp["longitude"][i], parking, info).add_to(map)
            except Exception as e:
                print(f"Error adding marker: {e}")

    TagFilterButton(dataframe['fee'].unique().tolist()).add_to(map)
    folium.Circle([start_lat, start_lon],
                    color='tomato',
                    radius=10*1000
                    ).add_to(map)
    st_folium(map, width=700, height = 550)

def mk_map1(dataframe, value):
    temp = dataframe[dataframe['stationName'] == value]
    if temp.empty:
        return

    parking = temp['fee'].iloc[0]
    loc_lat = temp['latitude'].iloc[0]
    loc_lon = temp['longitude'].iloc[0]

    def get_marker(lat, lon, info):
        colors = {"N":"#FF6F61", "Y":"#1E90FF"}
        return folium.CircleMarker(location=[lat, lon],
                                    radius=5, 
                                    fill_opacity=0.8, 
                                    fill_color=colors[parking],  
                                    color=colors[parking], 
                                    weight=1, 
                                    tooltip=info,
                                    tags=[parking]
                                    )

    map = folium.Map(location=[loc_lat, loc_lon], 
                        tiles="CartoDB positron", zoom_start=11)

    try:
        if parking == "N":
            info = f"""
                <font size=2.5>{value} </font> <br>
                <font size=2.2>주소: {temp['address'].values[0]} </font> <br>
                <font size=1.6>이용시간: {temp['useHour'].values[0]} </font> <br>
                <font size=1.6>전화번호: {temp['telNum'].values[0]} </font> <br>
                <font size=1.6>주차료: NO </font>
                """
        else:
            info = f"""
                <font size=2.5>{value} </font> <br>
                <font size=2.2>주소: {temp['address'].values[0]} </font> <br>
                <font size=1.6>이용시간: {temp['useHour'].values[0]} </font> <br>
                <font size=1.6>전화번호: {temp['telNum'].values[0]} </font> <br>
                <font size=1.6>주차료: YES </font>
                """
        get_marker(loc_lat, loc_lon, info).add_to(map)
    except Exception as e:
        print(f"Error adding marker: {e}")

    TagFilterButton(dataframe['fee'].unique().tolist()).add_to(map)
    folium.Circle([loc_lat, loc_lon],
                    color='tomato',
                    radius=10*700
                    ).add_to(map)
    st_folium(map, width=700, height = 550)

show_pages(
    [
        Page("video.py", "Video", "📼"),
        Page("map.py", "Map", "🗺️"),
        Page("layout.py", "FAQ", "❓")  
    ]
)

with st.sidebar:
    search = st.text_input("충전소 검색")
    if search:
        df_search = df[df['stationName'].str.contains(search)]
        if len(df_search) == 0:
            st.markdown(":red[다른 충전소를 검색해주세요]")
        else:
            df_search.reset_index(inplace = True)
            button = st.button("📜", help = "검색한 충전소 목록")
            if button:
                st.dataframe(df_search['stationName'])
    select_region = st.selectbox("지역", ['선택', '전국'] + admin_dist)
    if select_region == '전국':
        select_all = st.selectbox("선택", ['선택'] + df['stationName'].tolist())
        button = st.button("📜", help = f'{select_region} 충전소 목록')
        if button:
            st.dataframe(df['stationName'])
    for i in admin_dist:
        if select_region == i:
            temp = df[df['address'].str.contains(i)]
            temp.reset_index(inplace = True)
            select_part = st.selectbox("선택", ['선택'] + temp['stationName'].tolist())
            button = st.button('📜', help = f'{select_region} 충전소 목록')
            if button:
                st.dataframe(temp['stationName'])

# 검색어 입력시 지도
if search:
    select_region, select_all, select_part = '선택', '선택', '선택'
    if len(df_search) == 0:
        st.markdown(":red[검색 결과가 없습니다.]")
    else:
        st.markdown(f'### :blue-background[검색어: {search}]')
        start_lat, start_lon = df_search['latitude'][0], df_search['longitude'][0]
        mk_map(df_search, start_lat, start_lon)

# 전국 지도
if select_region == '전국':
    start_lat, start_lon = 37.466613, 126.889249
    if select_all and select_all != '선택':
        st.markdown(f'### :blue-background[select_all]')
        mk_map1(df, select_all) 
    st.markdown(f"### :blue-background[지역: {select_region}]")
    mk_map(df, start_lat, start_lon)

# 다른 지역 선택시 지도
for i in admin_dist:
    if select_region == i: 
        temp = df[df['address'].str.contains(i)]
        temp.reset_index(inplace = True)
        start_lat, start_lon = temp['latitude'][0], temp['longitude'][0]
        if select_part and select_part != '선택':
            st.markdown(f'### :blue-background[{select_part}]')
            mk_map1(temp, select_part)
        st.markdown(f"### :blue-background[지역: {select_region}]")
        mk_map(temp, start_lat, start_lon)