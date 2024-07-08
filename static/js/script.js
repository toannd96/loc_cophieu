$(document).ready(function() {
    // Function to populate industry dropdown
    function populateIndustryDropdown() {
        $.get('/industries', function(data) {
            var options = data.map(function(industry) {
                return `<option>${industry}</option>`;
            });
            $('#industrySelect').html(options.join(''));
        });
    }

    // Function to populate group dropdown
    function populateGroupDropdown() {
        $.get('/groups', function(data) {
            var options = data.map(function(group) {
                return `<option>${group}</option>`;
            });
            $('#groupSelect').html(options.join(''));
        });
    }

    // Function to populate signal categories
    function populateSignalCategories() {
        $.get('/signal_categories', function(data) {
            var options = data.map(function(category) {
                return `<option>${category}</option>`;
            });
            $('#signalCategorySelect').html(options.join(''));
            // Trigger change event to populate signals initially based on default category
            var defaultCategory = $('#signalCategorySelect').val();
            populateSignals(defaultCategory);
        });
    }

    var signalMappings = {
        'ma5_cross_up': 'Giá cắt lên đường MA5',
        'ma5_cross_down': 'Giá cắt xuống đường MA5',

        'ma5_above': 'Giá nằm trên đường MA5',
        'ma5_below': 'Giá nằm dưới đường MA5',

        'ma10_cross_up': 'Giá cắt lên đường MA10',
        'ma10_cross_down': 'Giá cắt xuống đường MA10',

        'ma10_above': 'Giá nằm trên đường MA10',
        'ma10_below': 'Giá nằm dưới đường MA10',

        'ma20_cross_up': 'Giá cắt lên đường MA20',
        'ma20_cross_down': 'Giá cắt xuống đường MA20',

        'ma20_above': 'Giá nằm trên đường MA20',
        'ma20_below': 'Giá nằm dưới đường MA20',

        'ma50_cross_up': 'Giá cắt lên đường MA50',
        'ma50_cross_down': 'Giá cắt xuống đường MA500',

        'ma50_above': 'Giá nằm trên đường MA50',
        'ma50_below': 'Giá nằm dưới đường MA50',

        'ma100_cross_up': 'Giá cắt lên đường MA100',
        'ma100_cross_down': 'Giá cắt xuống đường MA100',

        'ma100_above': 'Giá nằm trên đường MA100',
        'ma100_below': 'Giá nằm dưới đường MA100',

        'ma200_cross_up': 'Giá cắt lên đường MA200',
        'ma200_cross_down': 'Giá cắt xuống đường MA200',

        'ma200_above': 'Giá nằm trên đường MA200',
        'ma200_below': 'Giá nằm dưới đường MA200',

        'macd_cross_up': 'Đường MACD cắt lên đường tín hiệu',
        'macd_cross_down': 'Đường MACD cắt xuống đường tín hiệu',

        'bb_breakout_upper': 'Giá vượt ra ngoài biên trên',
        'bb_breakout_lower': 'Giá vượt ra ngoài biên dưới',

        'bb_upper': 'Giá chạm dải biên trên',
        'bb_lower': 'Giá chạm dải biên dưới',

        'rsi_overbought': 'RSI >= 70',
        'rsi_oversold': 'RSI <= 30',

        'price5_high_breakout': 'Các mã có giá vượt đỉnh tuần',
        'price5_low_breakout': 'Các mã có giá thủng đáy tuần',

        'price21_high_breakout': 'Các mã có giá vượt đỉnh tháng',
        'price21_low_breakout': 'Các mã có giá thủng đáy tháng',

        'price63_high_breakout': 'Các mã có giá vượt đỉnh quý',
        'price63_low_breakout': 'Các mã có giá thủng đáy quý',
        
        'price126_high_breakout': 'Các mã có giá vượt đỉnh 6 tháng',
        'price126_low_breakout': 'Các mã có giá thủng đáy 6 tháng',
    };

    // Function to populate signals based on selected category
    function populateSignals(category) {
        $.get(`/signals/${category}`, function(data) {
            var options = data.map(function(signal) {
                return `<option value="${signal}">${signalMappings[signal]}</option>`;
            });
            $('#signalSelect').html(options.join(''));
        });
    }

    // Event listener for signal category selection
    $('#signalCategorySelect').change(function() {
        var selectedCategory = $(this).val();
        populateSignals(selectedCategory);
    });

    // Biến để lưu số lượng tín hiệu đã chọn
    var selectedSignalsCount = 0;

    // Function để cập nhật số lượng tín hiệu đã chọn
    function updateSelectedSignalsCount() {
        $('#selectedSignalsHeader').text(`Tín hiệu đã chọn (${selectedSignalsCount})`);
    }

    // Event listener for adding selected signal
    $('#addSignalButton').click(function() {
        var selectedSignal = $('#signalSelect').val();
        if (selectedSignal) {
            var listItem = `<li class="list-group-item">${signalMappings[selectedSignal]} <button class="btn btn-sm btn-danger float-right remove-signal" data-signal="${selectedSignal}">x</button></li>`;
            $('#selectedSignals').append(listItem);
            selectedSignalsCount++; // Tăng số lượng tín hiệu đã chọn
            updateSelectedSignalsCount(); // Cập nhật hiển thị số lượng
        }
    });


    // Event listener for removing selected signal
    $('#selectedSignals').on('click', '.remove-signal', function() {
        var signalToRemove = $(this).data('signal');
        $(this).parent().remove();
        selectedSignalsCount--; // Giảm số lượng tín hiệu đã chọn
        updateSelectedSignalsCount(); // Cập nhật hiển thị số lượng
    });

    // Event listener for search button click
    $('#searchButton').click(function() {
        var industry = $('#industrySelect').val();
        var group = $('#groupSelect').val();
        var signal = $('#selectedSignals li').map(function() {
            return $(this).find('button').data('signal');
        }).get();

        // Build query string for signals
        var queryString = $.param({ industry: industry, group: group, signal: signal }, true);

        // Hiển thị spinner
        $('#loadingSpinner').show();

        $('#companyCount').html(`Tìm thấy <strong>0</strong> công ty phù hợp`);

        // Xóa hết dữ liệu hiện tại trên bảng
        $('#resultsTable tbody').empty();

        $.ajax({
            url: '/stocks',
            method: 'GET',
            data: queryString,
            success: function(response) {
                var total = response.paging.total;
                $('#companyCount').html(`Tìm thấy <strong>${total}</strong> công ty phù hợp`);
    
                var rows = response.results.map(function(result) {
                    return `
                        <tr>
                            <td>${result.symbol}</td>
                            <td>${result.company_name}</td>
                            <td>${result.industry_name}</td>
                            <td>${result.close_price}</td>
                            <td>${result.volume}</td>
                        </tr>
                    `;
                });
                // Thêm dữ liệu mới vào bảng
                $('#resultsTable tbody').html(rows.join(''));

                // Ẩn spinner
                $('#loadingSpinner').hide();
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);

                // Ẩn spinner khi có lỗi
                $('#loadingSpinner').hide();
            }
        });
    });

    // Initial population on page load
    populateIndustryDropdown();
    populateGroupDropdown();
    populateSignalCategories();
});
