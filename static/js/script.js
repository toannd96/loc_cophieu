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

    // Function to populate signals based on selected category
    function populateSignals(category) {
        $.ajax({
            url: `/signals/${category}`,
            method: 'GET',
            success: function(data) {
                var part1Options = Object.keys(data.part1 || {}).map(function(key) {
                    return `<option value="${data.part1[key]}">${key}</option>`;
                });
                var part2Options = Object.keys(data.part2 || {}).map(function(key) {
                    return `<option value="${data.part2[key]}">${key}</option>`;
                });
                var part3Options = Object.keys(data.part3 || {}).map(function(key) {
                    return `<option value="${data.part3[key]}">${key}</option>`;
                });
    
                $('#signalSelect1').html(part1Options.join(''));
                $('#signalSelect2').html(part2Options.join(''));
                $('#signalSelect3').html(part3Options.join(''));
            },
            error: function(error) {
                console.log('Error fetching signals:', error);
            }
        });
    }

    // Event listener for signal category selection
    $('#signalCategorySelect').change(function() {
        var selectedCategory = $(this).val();
        populateSignals(selectedCategory);
    });

    // Biến để lưu số lượng tín hiệu đã chọn
    var selectedSignalsCount = 0;

    // Biến để lưu các tín hiệu đã chọn
    var selectedSignals = {};

    // Function để cập nhật số lượng tín hiệu đã chọn
    function updateSelectedSignalsCount() {
        selectedSignalsCount = Object.keys(selectedSignals).length;
        $('#selectedSignalsHeader').text(`Tín hiệu đã chọn (${selectedSignalsCount})`);
    }

    // Event listener for adding selected signal
    $('#addSignalButton').click(function() {
        var selectedSignal1 = $('#signalSelect1').val();
        var selectedSignal2 = $('#signalSelect2').val();
        var selectedSignal3 = $('#signalSelect3').val();

        // Kiểm tra tín hiệu đã được chọn trước đó
        var combinedSignal = [selectedSignal1, selectedSignal2, selectedSignal3].filter(Boolean).join('_');
        if (selectedSignals[combinedSignal]) {
            alert('Tín hiệu này đã được chọn trước đó.');
            return;
        }

        // Thêm tín hiệu vào danh sách đã chọn
        selectedSignals[combinedSignal] = true;

        // Hiển thị tín hiệu đã chọn trên giao diện
        var displaySignals = [$('#signalSelect1 option:selected').text(), $('#signalSelect2 option:selected').text(), $('#signalSelect3 option:selected').text()].filter(Boolean).join(' ');
        var listItem = `<li class="list-group-item" data-signal="${combinedSignal}">${displaySignals} <button class="btn btn-sm btn-danger float-right remove-signal" data-toggle="tooltip" title="Bỏ chọn tín hiệu">x</button></li>`;
        $('#selectedSignalsContainer').append(listItem);

        // Cập nhật số lượng tín hiệu đã chọn
        updateSelectedSignalsCount();
    });

    // Event listener for removing selected signal
    $('#selectedSignalsContainer').on('click', '.remove-signal', function() {
        var listItem = $(this).parent();
        var signalToRemove = listItem.data('signal');

        // Xóa tín hiệu khỏi danh sách đã chọn
        delete selectedSignals[signalToRemove];

        // Xóa khỏi giao diện
        listItem.remove();

        // Cập nhật số lượng tín hiệu đã chọn
        updateSelectedSignalsCount();
    });

    // Event listener for search button click
    $('#searchButton').click(function() {
        var industry = $('#industrySelect').val();
        var group = $('#groupSelect').val();
        var signal = $('#selectedSignalsContainer li').map(function() {
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
                var total = response.total;
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

    // Function to get the current year
    function getCurrentYear() {
        return new Date().getFullYear();
    }

    // Create the footer note with the current year
    var footerNote = `
    <p class="text-muted small">
        Dữ liệu được truy xuất từ <a href="https://vnstocks.com/" target="_blank">Vnstock</a> - gói phần mềm Python phân tích thị trường chứng khoán Việt Nam. 
        (thinh-vu @ Github, Copyright (c) 2022-${getCurrentYear()}).
        <br></br>
        Dữ liệu bộ lọc được thống kê từ các tín hiệu kỹ thuật phát sinh trong vòng 24 giờ, tính đến thời điểm giao dịch cuối cùng gần nhất.
    </p>`;

    // Append the footer note to the div with id "footerNote"
    $('#footerNote').html(footerNote);

    // Initial population on page load
    populateIndustryDropdown();
    populateGroupDropdown();
    populateSignalCategories();
});
