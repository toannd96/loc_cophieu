![](https://github.com/toannd96/loc_cophieu/blob/master/static/img/loc_cophieu.png)

- Request API:
```
curl --location --request GET 'http://127.0.0.1:5000/stocks?signal=ma5_above&group=UPCOM&industry=Kim loại'
```
- Response API:
```
{
    "paging": {
        "from": 1,
        "limit": 100,
        "page": 1,
        "to": 2,
        "total": 2,
        "total_page": 1
    },
    "results": [
        {
            "close_price": 2.1,
            "company_name": "Công ty Cổ phần Sản xuất Xuất nhập khẩu Inox Kim Vĩ",
            "date": "2024-07-08 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "KVC",
            "volume": 133000
        },
        {
            "close_price": 11.0,
            "company_name": "Công ty Cổ phần Gang thép Cao Bằng",
            "date": "2024-07-08 00:00:00",
            "industry_name": "Kim loại",
            "symbol": "CBI",
            "volume": 100
        }
    ]
} 
```
- Cài đặt:
    - [python-latest-version-install](https://cloudbytes.dev/snippets/upgrade-python-to-latest-version-on-ubuntu-linux)
