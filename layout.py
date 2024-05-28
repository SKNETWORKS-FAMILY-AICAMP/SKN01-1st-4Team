from pyparsing import empty
import streamlit as st
import pandas as pd
import time
from sqlalchemy import create_engine
import geopandas as gpd
import streamlit as st
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
import geojson
from shapely.geometry import shape
from keplergl import KeplerGl
import json
from streamlit.components.v1 import html

# <-- 페이지 레이아웃 -->
st.set_page_config(
    layout="wide",
    page_title="TEAM_4",
    page_icon="./img/TEAM_4_wide_image_resized.png"
    )
empty1,con1,empty2 = st.columns([0.1,1.0,0.1])
empyt1,con2,con3,empty2 = st.columns([0.1,0.4,0.6,0.1])
empyt1,con4,empty2 = st.columns([0.1,1.0,0.1])


### [DB 연결]
db_connection_str = 'mysql+pymysql://root@192.168.0.30:3306/cardb'
db_connection = create_engine(db_connection_str)
db_conn = db_connection.connect()
# --------------------------------------------------------------------

def main() :
    # <-- 왼쪽 여백 -->
    with empty1 :
        empty() # 여백부분1
   
    # <-- con1 : 헤더 -->
    with con1 :
        st.image("./img/TEAM_4_wide_image.png")
        st.markdown('<h1 style="text-align:center">FAQ</h1>', unsafe_allow_html=True)
        st.divider()

    # <-- con2 : 지도 -->
    with con2 :
        with st.expander("**3D** 전기차 과거와 현재", expanded=True):
            past_now_3d()
        with st.expander("**3D** 전기차 및 내연기관"):
            electro_gasoline_3d()
        with st.expander("전국 자동차 등록 현황"):
            all_car_map()

    # <-- con3 : FAQ -->
    with con3 :
        # sk일렉링크 FAQ
        with st.expander("**SK 일렉링크 관련 FAQ**"):
            df2 = pd.read_sql_query("SELECT * FROM faq", db_conn)
            for i in range(len(df2)):
                fag_write(df2.iloc[i, 1], df2.iloc[i, 2])

        st.markdown("<br>", unsafe_allow_html=True)

        # 생성 FAQ
        df1 = pd.read_sql_query("SELECT * FROM charger_function", db_conn).T
        df1.rename(columns={0:"설명", 1:"설명"}, inplace=True)
        fag_write_w_img("**:red[SK 일렉링크] 충전기** 구성이 어떻게 되나요?", df1)

        df1_1 = pd.read_sql_query("SELECT * FROM evcar_mileage", db_conn)
        df1_1_txt = f"- **{df1_1['ev_model'][0]}**는  **{df1_1['range(km)'][0]}** 주행할 수 있습니다. \n"
        df1_1_txt1 = f"- **{df1_1['ev_model'][1]}**는  **{df1_1['range(km)'][1]}** 주행할 수 있습니다. \n"
        df1_1_txt2 = f"- **{df1_1['ev_model'][2]}**는  **{df1_1['range(km)'][2]}** 주행할 수 있습니다. \n"
        df1_1_txt3 = "\n\n \>\>\> 더 많은 모델을 궁금하다면, 아래의 표를 참조해주세요. \n \n"

        fag_write("한 번 충전으로 주행거리가 가장 긴 전기차는 무엇인가요?", df1_1_txt, df1_1_txt1, df1_1_txt2, df1_1_txt3, df1_1)

        df3 = pd.read_sql_query("SELECT * FROM charger_model", db_conn)
        df3_1_txt = f"""
        **{df3["type"].unique()[0]} 충전기 모델**은 다음과 같습니다. \n"""
        df3_1_txt1 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][0]} \n"""
        df3_1_txt2 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][1]} \n"""
        df3_1_txt3 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][2]} \n"""
        df3_1_txt4 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][3]} \n"""
        df3_1_txt5 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][4]} \n"""
        df3_1_txt6 = f"""- {df3[df3["type"]==df3["type"].unique()[0]]["model"][5]} \n"""
        # df3_1_txt2 = f"- "
        # df3_1_txt3 = "\n\n \>\>\> 더 많은 모델을 궁금하다면, 아래의 표를 참조해주세요. \n \n"
        fag_write("SK 일렉링크 충전기 중에 완속 모델은 어떤 것이 있나요?", df3_1_txt, df3_1_txt1, df3_1_txt2, df3_1_txt3, df3_1_txt4, df3_1_txt5, df3_1_txt6)

        df4 = pd.read_sql_query("SELECT * FROM charging_station", db_conn)
        df4_txt1 = "**충전기 타입**은 다음과 같습니다. \n \n"
        df4_txt2 = f'- {str(df4["charge_system"].unique().tolist())[1:-1]}'
        fag_write("우리나라에 있는 충전기 타입에 어떤 종류가 있나요?", df4_txt1, df4_txt2)

    # <-- con4 : 미정 -->
    with con4 :
        empty()
        # st.title("bottom")

    # <-- 오른쪽 여백 -->
    with empty2 :
        empty()


### [FAQ 함수 정의]
def fag_write(question, *answers):
    # 텍스트 효과 - 타자기st
    def txteff_typewriter(*args):
        for data in args:
            if type(data) == str:
                for word in data.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            else:
                yield data
                time.sleep(0.02)

    with st.container():
        st.markdown("""
        <style>
        div[data-testid="stButton_container"] > button > span {
            text-align: left;
        }
        </style>
        """, unsafe_allow_html=True)

    if st.button(f"**Q** &nbsp; :grey[{question}]", use_container_width=200):
        st.write_stream(txteff_typewriter(*answers))

def fag_write_w_img(question, df):
    # 텍스트 효과 - 타자기st
    def txteff_typewriter(*args):
        for data in args:
            if type(data) == str:
                for word in data.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            else:
                yield data
                time.sleep(0.02)

    if st.button(f"**Q** &nbsp; :grey[{question}]", use_container_width=200):
        
        st.markdown("""
        <style>
        div[data-testid="stButton_container"] > button > span {
            text-align: left;
        }
        </style>
        """, unsafe_allow_html=True)
        with st.container():
            col1, col2 = st.columns([0.4, 0.6])
            with col1:
                st.image(f"./img/charger1.png")
            with col2:
                st.write_stream(txteff_typewriter(df.iloc[1:,0]))

        with st.container():
            col1, col2 = st.columns([0.4, 0.6])
            with col1:
                st.image(f"./img/charger2.png")
            with col2:
                st.write_stream(txteff_typewriter(df.iloc[1:,1]))
# ------------------------------------------------------------------    
def all_car_map():
    import streamlit as st
    import pandas as pd
    import geopandas as gpd
    from sqlalchemy import create_engine, text
    import geojson
    from shapely.geometry import shape
    from keplergl import KeplerGl
    import json
    from streamlit.components.v1 import html

    # MySQL 데이터베이스 연결 문자열
    db_connection_str = 'mysql+pymysql://root@127.0.0.1:3306/cardb?charset=utf8mb4'
    db_connection = create_engine(db_connection_str)

    # # Streamlit 애플리케이션 구성
    # st.title("전국 자동차 현황 조회")
    # st.write("DB Kepler.gl Streamlit 사용")

    # 카테고리 선택
    category = st.selectbox(
        '카테고리를 선택하세요',
        ('승용', '승합', '화물', '특수', '총계'),
        key='category',
        help="원하는 차량 종류를 선택하세요."
    )

    # 텍스트 입력 창 추가
    search_text = st.text_input(
        '지역을 입력하세요',
        value='',
        key='region',
        help="검색할 지역을 입력하세요."
    )

    # 데이터베이스에서 데이터 불러오기
    @st.cache_data
    def load_data():
        db_conn = db_connection.connect()
        select_query = text('''
            SELECT 
                region_name AS 지역,
                승용_관용, 
                승용_자가용, 
                승용_영업용, 
                승용_합계, 
                승합_관용, 
                승합_자가용, 
                승합_영업용, 
                승합_합계, 
                화물_관용, 
                화물_자가용, 
                화물_영업용, 
                화물_합계, 
                특수_관용, 
                특수_자가용, 
                특수_영업용, 
                특수_합계, 
                총계_관용, 
                총계_자가용, 
                총계_영업용, 
                총계_합계, 
                ST_AsGeoJSON(geom) as geom 
            FROM car_data;
        ''')
        result = db_conn.execute(select_query)
        rows = result.fetchall()

        # GeoDataFrame 생성
        data = []
        for row in rows:
            properties = {
                '지역': row[0],
                '승용_관용': row[1],
                '승용_자가용': row[2],
                '승용_영업용': row[3],
                '승용_합계': row[4],
                '승합_관용': row[5],
                '승합_자가용': row[6],
                '승합_영업용': row[7],
                '승합_합계': row[8],
                '화물_관용': row[9],
                '화물_자가용': row[10],
                '화물_영업용': row[11],
                '화물_합계': row[12],
                '특수_관용': row[13],
                '특수_자가용': row[14],
                '특수_영업용': row[15],
                '특수_합계': row[16],
                '총계_관용': row[17],
                '총계_자가용': row[18],
                '총계_영업용': row[19],
                '총계_합계': row[20]
            }
            geometry = shape(geojson.loads(row[21]))
            properties['geometry'] = geometry
            data.append(properties)

        gdf = gpd.GeoDataFrame(data)
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)  # 지오메트리 단순화

        db_conn.close()
        return gdf

    # 데이터 불러오기
    gdf = load_data()

    # 카테고리와 지역에 따른 필터링
    if search_text:
        gdf = gdf[gdf['지역'].str.contains(search_text)]

    # 선택된 카테고리의 데이터만 남기기
    category_columns = {
        '승용': ['승용_관용', '승용_자가용', '승용_영업용', '승용_합계'],
        '승합': ['승합_관용', '승합_자가용', '승합_영업용', '승합_합계'],
        '화물': ['화물_관용', '화물_자가용', '화물_영업용', '화물_합계'],
        '특수': ['특수_관용', '특수_자가용', '특수_영업용', '특수_합계'],
        '총계': ['총계_관용', '총계_자가용', '총계_영업용', '총계_합계']
    }

    columns_to_keep = ['지역', 'geometry'] + category_columns[category]
    gdf = gdf[columns_to_keep]

    # Kepler.gl 지도 설정
    map_1 = KeplerGl(height=600)
    map_1.add_data(data=gdf, name="car_data")

    # 대한민국 중심 좌표로 초기 뷰포트 설정
    config = {
        "version": "v1",
        "config": {
            "visState": {},
            "mapState": {
                "bearing": 0,
                "dragRotate": False,
                "latitude": 36.5,  # 대한민국 중심 위도
                "longitude": 127.5,  # 대한민국 중심 경도
                "pitch": 0,
                "zoom": 5,  # 적절한 줌 레벨 설정
                "isSplit": False
            },
            "mapStyle": {}
        }
    }

    map_1.config = config

    # Kepler.gl 지도 렌더링
    map_1.save_to_html(file_name="keplergl_map.html")
    with open("keplergl_map.html", "r", encoding="utf-8") as f:
        html_data = f.read()

    # Streamlit의 components.html 메서드를 사용하여 Kepler.gl 지도 렌더링
    st.components.v1.html(html_data, height=600)

def electro_gasoline_3d():        
    # 대한민국의 위도와 경도
    korea_latitude = 35.9078
    korea_longitude = 127.7669

    # 데이터베이스 연결 문자열
    db_connection_str = 'mysql+pymysql://root@127.0.0.1:3306/cardb?charset=utf8mb4'
    engine = create_engine(db_connection_str)

    # 데이터베이스에서 데이터를 가져오는 쿼리
    query = "SELECT * FROM gc_ec_car_data"

    # 데이터 가져오기
    df = pd.read_sql(query, engine)

    # 위도와 경도 값이 수치형으로 변환되었는지 확인
    df['위도'] = df['langtitude'].astype(float)
    df['경도'] = df['longitude'].astype(float)
    df['위도1'] = df['langtitude1'].astype(float)
    df['경도1'] = df['longitude1'].astype(float)

    # GeoDataFrame 생성 (전기차 데이터)
    gdf_ev = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['langtitude']))

    # GeoDataFrame 생성 (기름차 데이터)
    gdf_gas = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['langtitude']))

    # Kepler.gl을 사용하여 지도 시각화
    map_kepler = KeplerGl(height=800)
    map_kepler.add_data(data=gdf_ev, name='Electric Vehicles')
    map_kepler.add_data(data=gdf_gas, name='Gasoline Vehicles')

    # Kepler.gl 설정
    config = {
        "version": "v1",
        "config": {
            "mapState": {
                "bearing": 0,
                "latitude": korea_latitude,
                "longitude": korea_longitude,
                "pitch": 45,  # 3D 맵 활성화를 위한 pitch 설정
                "zoom": 6  # 줌 레벨 조정
            },
            "visState": {
                "filters": [],
                "layers": [
                    {
                        "id": "electric-vehicles-layer",
                        "type": "hexagon",
                        "config": {
                            "dataId": "Electric Vehicles",
                            "label": "Electric Vehicles",
                            "color": [255, 153, 31],
                            "columns": {
                                "lat": "langtitude",
                                "lng": "longitude"
                            },
                            "visConfig": {
                                "opacity": 0.8,
                                "elevationScale": 10.0,  # 크게 조정된 elevationScale 값
                                "enable3d": True,  # Height 기본적으로 On
                                "colorRange": {
                                    "name": "ColorBrewer YlOrRd-9",
                                    "type": "sequential",
                                    "category": "ColorBrewer",
                                    "colors": ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c", "#bd0026", "#800026"]
                                },
                                "radius": 1000,
                                "coverage": 1,
                                "sizeRange": [0, 2000],
                                "heightRange": [0, 2000]
                            },
                            "hidden": False,
                            "isVisible": True,
                            "textLabel": [
                                {
                                    "field": None,
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center"
                                }
                            ]
                        },
                        "visualChannels": {
                            "colorField": {"name": "sum_electronic", "type": "integer"},
                            "colorScale": "quantile",
                            "sizeField": {"name": "sum_electronic", "type": "integer"},
                            "sizeScale": "linear"
                        }
                    },
                    {
                        "id": "gasoline-vehicles-layer",
                        "type": "hexagon",
                        "config": {
                            "dataId": "Gasoline Vehicles",
                            "label": "Gasoline Vehicles",
                            "color": [23, 184, 190],
                            "columns": {
                                "lat": "langtitude1",
                                "lng": "longitude1"
                            },
                            "visConfig": {
                                "opacity": 0.8,
                                "elevationScale": 30.0,  # 크게 조정된 elevationScale 값
                                "enable3d": True,  # Height 기본적으로 On
                                "colorRange": {
                                    "name": "ColorBrewer YlGnBu-9",
                                    "type": "sequential",
                                    "category": "ColorBrewer",
                                    "colors": ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"]
                                },
                                "radius": 1000,
                                "coverage": 1,
                                "sizeRange": [0, 2000],
                                "heightRange": [0, 2000]
                            },
                            "hidden": False,
                            "isVisible": True,
                            "textLabel": [
                                {
                                    "field": None,
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center"
                                }
                            ]
                        },
                        "visualChannels": {
                            "colorField": {"name": "sum_gasoline", "type": "integer"},
                            "colorScale": "quantile",
                            "sizeField": {"name": "sum_gasoline", "type": "integer"},
                            "sizeScale": "linear"
                        }
                    }
                ],
                "interactionConfig": {
                    "tooltip": {
                        "fieldsToShow": {
                            "Electric Vehicles": [
                                {"name": "시도", "format": None},
                                {"name": "sum_electronic", "format": None}
                            ],
                            "Gasoline Vehicles": [
                                {"name": "시도", "format": None},
                                {"name": "sum_gasoline", "format": None}
                            ]
                        },
                        "enabled": True
                    }
                },
                "layerBlending": "normal",
                "splitMaps": []
            }
        }
    }

    map_kepler.config = config

    # Kepler.gl 지도를 HTML로 저장
    map_kepler.save_to_html(file_name='kepler_map.html')

    # HTML 파일을 Streamlit에서 iframe으로 표시
    with open('kepler_map.html', 'r', encoding='utf-8') as f:
        map_html = f.read()

    st.components.v1.html(map_html, height=800)

def past_now_3d():
    # 대한민국의 위도와 경도
    korea_latitude = 35.9078
    korea_longitude = 127.7669

    # 데이터베이스 연결 문자열
    db_connection_str = 'mysql+pymysql://root@127.0.0.1:3306/cardb?charset=utf8mb4'
    engine = create_engine(db_connection_str)

    # 데이터베이스에서 데이터를 가져오는 쿼리
    query = "SELECT * FROM gc_ec_car_data"

    # 데이터 가져오기
    df = pd.read_sql(query, engine)

    # 위도와 경도 값이 수치형으로 변환되었는지 확인
    df['위도'] = df['langtitude'].astype(float)
    df['경도'] = df['longitude'].astype(float)
    df['위도1'] = df['langtitude1'].astype(float)
    df['경도1'] = df['longitude1'].astype(float)

    # GeoDataFrame 생성 (전기차 데이터)
    gdf_ev = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['langtitude']))

    # GeoDataFrame 생성 (기름차 데이터)
    gdf_gas = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['langtitude']))

    # Kepler.gl을 사용하여 지도 시각화
    map_kepler = KeplerGl(height=800)
    map_kepler.add_data(data=gdf_ev, name='Past Electric Vehicles')
    map_kepler.add_data(data=gdf_gas, name='Now Electric Vehicles')

    # Kepler.gl 설정
    config = {
        "version": "v1",
        "config": {
            "mapState": {
                "bearing": 0,
                "latitude": korea_latitude,
                "longitude": korea_longitude,
                "pitch": 45,  # 3D 맵 활성화를 위한 pitch 설정
                "zoom": 6  # 줌 레벨 조정
            },
            "visState": {
                "filters": [],
                "layers": [
                    {
                        "id": "Past electric layer",
                        "type": "hexagon",
                        "config": {
                            "dataId": "Past Electric Vehicles",
                            "label": "Past Electric Vehicles",
                            "color": [255, 153, 31],
                            "columns": {
                                "lat": "langtitude",
                                "lng": "longitude"
                            },
                            "visConfig": {
                                "opacity": 0.8,
                                "elevationScale": 5.0,  # 크게 조정된 elevationScale 값
                                "enable3d": True,  # Height 기본적으로 On
                                "colorRange": {
                                    "name": "ColorBrewer YlOrRd-9",
                                    "type": "sequential",
                                    "category": "ColorBrewer",
                                    "colors": ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8d3c", "#fc4e2a", "#e31a1c", "#bd0026", "#800026"]
                                },
                                "radius": 1000,
                                "coverage": 1,
                                "sizeRange": [0, 2000],
                                "heightRange": [0, 2000]
                            },
                            "hidden": False,
                            "isVisible": True,
                            "textLabel": [
                                {
                                    "field": None,
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center"
                                }
                            ]
                        },
                        "visualChannels": {
                            "colorField": {"name": "sum_electronic", "type": "integer"},
                            "colorScale": "quantile",
                            "sizeField": {"name": "old_sum_electronic", "type": "integer"},
                            "sizeScale": "linear"
                        }
                    },
                    {
                        "id": "Now-Electric-layer",
                        "type": "hexagon",
                        "config": {
                            "dataId": "Now Electric Vehicles",
                            "label": "Now Electric Vehicles",
                            "color": [23, 184, 190],
                            "columns": {
                                "lat": "langtitude1",
                                "lng": "longitude1"
                            },
                            "visConfig": {
                                "opacity": 0.8,
                                "elevationScale": 10.0,  # 크게 조정된 elevationScale 값
                                "enable3d": True,  # Height 기본적으로 On
                                "colorRange": {
                                    "name": "ColorBrewer YlGnBu-9",
                                    "type": "sequential",
                                    "category": "ColorBrewer",
                                    "colors": ["#ffffd9", "#edf8b1", "#c7e9b4", "#7fcdbb", "#41b6c4", "#1d91c0", "#225ea8", "#253494", "#081d58"]
                                },
                                "radius": 1000,
                                "coverage": 1,
                                "sizeRange": [0, 2000],
                                "heightRange": [0, 2000]
                            },
                            "hidden": False,
                            "isVisible": True,
                            "textLabel": [
                                {
                                    "field": None,
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center"
                                }
                            ]
                        },
                        "visualChannels": {
                            "colorField": {"name": "sum_electronic", "type": "integer"},
                            "colorScale": "quantile",
                            "sizeField": {"name": "old_sum_electronic", "type": "integer"},
                            "sizeScale": "linear"
                        }
                    }
                ],
                "interactionConfig": {
                    "tooltip": {
                        "fieldsToShow": {
                            "Electric Vehicles": [
                                {"name": "시도", "format": None},
                                {"name": "sum_electronic", "format": None}
                            ],
                            "Gasoline Vehicles": [
                                {"name": "시도", "format": None},
                                {"name": "old_sum_electronic", "format": None}
                            ]
                        },
                        "enabled": True
                    }
                },
                "layerBlending": "normal",
                "splitMaps": []
            }
        }
    }

    map_kepler.config = config

    # Kepler.gl 지도를 HTML로 저장
    map_kepler.save_to_html(file_name='kepler_map.html')

    # HTML 파일을 Streamlit에서 iframe으로 표시
    with open('kepler_map.html', 'r', encoding='utf-8') as f:
        map_html = f.read()

    st.components.v1.html(map_html, height=800)


main()