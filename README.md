![](https://github.com/toannd96/loc_cophieu/blob/master/static/img/loc_cp.png)

- Request API:
```
curl --location --request GET 'http://127.0.0.1:5000/stocks?group=UPCOM&sector_name=Kim loại&check_period_hours=24&signal=ma5_above&signal=bb_upper'
```
- Response API:
```
{
    "results": [
        {
            "close_price": 4.2,
            "company_name": "Công ty Cổ phần Quốc tế Phương Anh",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "PAS",
            "volume": 255000
        },
        {
            "close_price": 22.0,
            "company_name": "Công ty Cổ phần Xích líp Đông Anh",
            "date": "2024-07-04 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "DFC",
            "volume": 0
        },
        {
            "close_price": 19.2,
            "company_name": "Công ty Cổ phần Mạ kẽm công nghiệp Vingal-Vnsteel",
            "date": "2024-07-04 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "VGL",
            "volume": 100
        },
        {
            "close_price": 18.4,
            "company_name": "Công ty Cổ phần Thép Thủ Đức - VNSTEEL",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TDS",
            "volume": 94500
        },
        {
            "close_price": 58.0,
            "company_name": "Công ty Cổ phần Kim loại màu Thái Nguyên - Vimico",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TMG",
            "volume": 100
        },
        {
            "close_price": 0.4,
            "company_name": "Công ty Cổ phần Hữu Liên Á Châu",
            "date": "2024-07-04 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "HLA",
            "volume": 0
        },
        {
            "close_price": 5.1,
            "company_name": "Công ty Cổ phần Tập đoàn HSV Việt Nam",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "HSV",
            "volume": 80500
        },
        {
            "close_price": 31.8,
            "company_name": "Công ty Cổ phần Tôn Đông Á",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "GDA",
            "volume": 266800
        },
        {
            "close_price": 10.8,
            "company_name": "Tổng Công ty Thép Việt Nam - Công ty Cổ phần",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TVN",
            "volume": 2824400
        },
        {
            "close_price": 19.0,
            "company_name": "Công ty Cổ phần Lưới thép Bình Tây",
            "date": "2024-07-04 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "VDT",
            "volume": 1
        },
        {
            "close_price": 4.4,
            "company_name": "Công ty Cổ phần Thép Tấm Lá Thống Nhất",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TNS",
            "volume": 23100
        },
        {
            "close_price": 1.1,
            "company_name": "Công ty Cổ phần Sức khỏe Hồi sinh Việt Nam",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "NHV",
            "volume": 9400
        },
        {
            "close_price": 0.3,
            "company_name": "Công ty Cổ phần Đầu tư Phát triển Sóc Sơn",
            "date": "2024-07-04 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "DPS",
            "volume": 0
        },
        {
            "close_price": 14.0,
            "company_name": "Công ty Cổ phần Thép Nhà Bè - VNSTEEL",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TNB",
            "volume": 400
        },
        {
            "close_price": 6.7,
            "company_name": "Công ty Cổ phần Gang thép Thái Nguyên",
            "date": "2024-07-05 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "TIS",
            "volume": 329300
        }
    ],
    "paging": {
        "from": 1,
        "limit": 100,
        "page": 1,
        "to": 15,
        "total": 15,
        "total_page": 1
    }
} 
```
- Cài đặt:
    - [python-latest-version-install](https://cloudbytes.dev/snippets/upgrade-python-to-latest-version-on-ubuntu-linux)
