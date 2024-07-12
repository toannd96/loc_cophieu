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

    // Signal mappings
    var signalMappings = {
        'Bollinger Band (20, 2)': {
            'part1': {
                'Giá': 'bb',
            },
            'part2': {
                'vượt ra ngoài': 'breakout',
                'chạm dải': 'touch'
            },
            'part3': {
                'biên trên': 'upper',
                'biên dưới': 'lower',
            }
        },
        'Moving Average (MA)': {
            'part1': {
                'Giá': 'ma',
            },
            'part2': {
                'cắt lên': 'cross_up',
                'cắt xuống': 'cross_down',
                'nằm trên': 'above',
                'nằm dưới': 'below',
            },
            'part3': {
                'MA10': '10',
                'MA20': '20',
                'MA50': '50',
                'MA100': '100',
                'MA200': '200',
            }
        },
        'MACD (9, 12, 26)': {
            'part1': {
                'Đường MACD': 'macd',
            },
            'part2': {
                'cắt lên': 'cross_up',
                'cắt xuống': 'cross_down',
            },
            'part3': {
                'đường tín hiệu': 'signal',
            }
        },
        'RSI (14)': {
            'part1': {
                'Giá trị RSI': 'rsi',
            },
            'part2': {
                'lớn hơn': 'gt',
                'nhỏ hơn': 'lt',
            },
            'part3': {
                '30': 'oversold',
                '70': 'overbought',
            }
        },
        'Giá': {
            'part1': {
                'Giá': 'price',
            },
            'part2': {
                'tăng vượt đỉnh': 'high_breakout',
                'giảm thủng đáy': 'low_breakout',
            },
            'part3': {
                'tuần': '5',
                'tháng': '21',
                'quý': '63',
                '6 tháng': '126'
            }
        },
    };

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

    // Function to populate signals based on selected category
    function populateSignals(category) {
        var signalParts = signalMappings[category] || {};
        var part1Options = Object.keys(signalParts.part1 || {}).map(function(key) {
            return `<option value="${signalParts.part1[key]}">${key}</option>`;
        });
        var part2Options = Object.keys(signalParts.part2 || {}).map(function(key) {
            return `<option value="${signalParts.part2[key]}">${key}</option>`;
        });
        var part3Options = Object.keys(signalParts.part3 || {}).map(function(key) {
            return `<option value="${signalParts.part3[key]}">${key}</option>`;
        });

        $('#signalSelect1').html(part1Options.join(''));
        $('#signalSelect2').html(part2Options.join(''));
        $('#signalSelect3').html(part3Options.join(''));
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
        var selectedSignal1 = $('#signalSelect1').val();
        var selectedSignal2 = $('#signalSelect2').val();
        var selectedSignal3 = $('#signalSelect3').val();
        if (selectedSignal1 && selectedSignal2 && selectedSignal3) {
            var displaySignal1 = $('#signalSelect1 option:selected').text();
            var displaySignal2 = $('#signalSelect2 option:selected').text();
            var displaySignal3 = $('#signalSelect3 option:selected').text();
            
            // Combine the signal parts correctly
            var combinedSignal = selectedSignal1;
            if (selectedSignal2) {
                combinedSignal += `_${selectedSignal2}`;
            }
            if (selectedSignal3) {
                combinedSignal += `_${selectedSignal3}`;
            }

            var listItem = `<li class="list-group-item" data-signal="${combinedSignal}">${displaySignal1} ${displaySignal2} ${displaySignal3} <button class="btn btn-sm btn-danger float-right remove-signal">x</button></li>`;
            $('#selectedSignals').append(listItem);
            selectedSignalsCount++; // Tăng số lượng tín hiệu đã chọn
            updateSelectedSignalsCount(); // Cập nhật hiển thị số lượng
        }
    });

    // Event listener for removing selected signal
    $('#selectedSignals').on('click', '.remove-signal', function() {
        $(this).parent().remove();
        selectedSignalsCount--; // Giảm số lượng tín hiệu đã chọn
        updateSelectedSignalsCount(); // Cập nhật hiển thị số lượng
    });

    // Event listener for search button click
    $('#searchButton').click(function() {
        var industry = $('#industrySelect').val();
        var group = $('#groupSelect').val();
        var signal = $('#selectedSignals li').map(function() {
            return $(this).data('signal');
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
