$(document).ready(function() {
    // Function to populate industry dropdown
    function populateIndustryDropdown() {
        var industries = [
            'Bia và đồ uống', 'Bán lẻ', 'Bảo hiểm nhân thọ', 'Bảo hiểm phi nhân thọ',
            'Bất động sản', 'Công nghiệp nặng', 'Du lịch & Giải trí', 'Dược phẩm',
            'Dịch vụ tài chính', 'Hàng cá nhân', 'Hàng công nghiệp', 'Hàng gia dụng',
            'Hàng hóa giải trí', 'Hóa chất', 'Khai khoáng', 'Kim loại',
            'Lâm nghiệp và Giấy', 'Ngân hàng', 'Nước & Khí đốt',
            'Phân phối thực phẩm & dược phẩm', 'Phần mềm & Dịch vụ Máy tính',
            'Sản xuất & Phân phối Điện', 'Sản xuất Dầu khí', 'Sản xuất thực phẩm',
            'Thiết bị và Dịch vụ Y tế', 'Thiết bị và Phần cứng',
            'Thiết bị, Dịch vụ và Phân phối Dầu khí', 'Thuốc lá', 'Truyền thông',
            'Tư vấn & Hỗ trợ Kinh doanh', 'Viễn thông cố định',
            'Viễn thông di động', 'Vận tải', 'Xây dựng và Vật liệu',
            'Ô tô và phụ tùng', 'Điện tử & Thiết bị điện'
        ];

        var options = industries.map(industry => `<option>${industry}</option>`);
        $('#industrySelect').html(options.join(''));
    }

    // Function to populate exchange dropdown
    function populateExchangeDropdown() {
        var exchanges = [
            'HOSE', 'VN30', 'VNMidCap', 'VNSmallCap', 'VNAllShare', 'VN100',
            'ETF', 'HNX', 'HNX30', 'HNXCon', 'HNXFin', 'HNXLCap', 'HNXMSCap',
            'HNXMan', 'UPCOM', 'FU_INDEX'
        ];

        var options = exchanges.map(exchange => `<option>${exchange}</option>`);
        $('#exchangeSelect').html(options.join(''));
    }

    // Function to populate signal categories
    function populateSignalCategories() {
        var categories = [
            'MACD', 'Bollinger Band', 'RSI'
        ];

        var options = categories.map(category => `<option>${category}</option>`);
        $('#signalCategorySelect').html(options.join(''));
    }

    // Function to populate signals based on selected category
    function populateSignals(category) {
        var signalsMap = {
            'MACD': ['Đường MACD cắt lên đường tín hiệu', 'Đường MACD cắt xuống đường tín hiệu'],
            'Bollinger Band': ['Giá vượt ra ngoài biên trên', 'Giá vượt ra ngoài biên dưới', 'Giá chạm dải biên trên', 'Giá chạm dải biên dưới'],
            'RSI': ['RSI >= 70', 'RSI <= 30']
        };

        var signals = signalsMap[category] || [];
        var options = signals.map(signal => `<option>${signal}</option>`);
        $('#signalSelect').html(options.join(''));
    }

    // Event listener for signal category selection
    $('#signalCategorySelect').change(function() {
        var selectedCategory = $(this).val();
        populateSignals(selectedCategory);
    });

    // Event listener for adding selected signal
    $('#addSignalButton').click(function() {
        var selectedSignal = $('#signalSelect').val();
        if (selectedSignal) {
            var listItem = `<li class="list-group-item">${selectedSignal} <button class="btn btn-sm btn-danger float-right remove-signal">x</button></li>`;
            $('#selectedSignals').append(listItem);
        }
    });

    // Event listener for removing selected signal
    $('#selectedSignals').on('click', '.remove-signal', function() {
        $(this).parent().remove();
    });

    // Event listener for search button click
    $('#searchButton').click(function() {
        // Replace with actual search logic and results population
        var results = [
            {
                "symbol": "BID",
                "company_name": "Ngân hàng Thương mại Cổ phần Đầu tư và Phát triển Việt Nam",
                "industry_name": "Ngân hàng",
                "close_price": 47.3,
                "volume": 2668392
            },
            {
                "symbol": "PLX",
                "company_name": "Tập đoàn Xăng dầu Việt Nam",
                "industry_name": "Sản xuất Dầu khí",
                "close_price": 43.9,
                "volume": 6019356
            }
        ];

        var total = results.length;
        $('#companyCount').text(`Tìm thấy ${total} công ty phù hợp`);

        var rows = results.map(result => `
            <tr>
                <td>${result.symbol}</td>
                <td>${result.company_name}</td>
                <td>${result.industry_name}</td>
                <td>${result.close_price}</td>
                <td>${result.volume}</td>
            </tr>
        `);
        $('#resultsTable tbody').html(rows.join(''));
    });

    // Initial population on page load
    populateIndustryDropdown();
    populateExchangeDropdown();
    populateSignalCategories();
});
