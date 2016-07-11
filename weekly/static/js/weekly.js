/**
 * Created by Nova on 2016/6/27.
 */

function yyyymm() {
    var now = new Date();
    var dateStr = now.getYear()+1900+'-';
    if (now.getMonth() < 9) dateStr += '0';
    dateStr += (now.getMonth()+1);
    return dateStr;
}

function yyyymmdd() {
    var now = new Date();
    var dateStr = now.getYear()+1900;
    dateStr += '-'
    if (now.getMonth() < 9) dateStr += '0';
    dateStr += (now.getMonth()+1);
    dateStr += '-';
    if (now.getDate() < 9) dateStr += '0';
    dateStr += (now.getDate());
    return dateStr;
}

function setupDatePicker(query, format) {
    query = '.'+query;
    if (format == 'yyyy-mm') {
        $(query).datetimepicker({
            format: format,
            minView: 'year',
            startView: 'year',
            language: 'zh-CN',
            autoclose: true,
        });

        $(query).each(function(idx, input) {
            var val = input.value;
            console.log(idx, val);
            if (val == undefined || val.length == 0) {
                input.value = yyyymm();
            }
        });
    } else {
        $(query).datetimepicker({
            format: format,
            minView: 'month',
            startView: 'month',
            language: 'zh-CN',
            autoclose: true,
        });
        $(query).each(function(idx, input) {
            var val = input.value;
            console.log(idx, val);
            if (val == undefined || val.length == 0) {
                input.value = yyyymmdd();
            }
        });
    }
}

function insertItem(type) {
    if (type == 'finished') {
        var html = '\
            <tr class="finished">\
                <td><textarea class="form-control" rows="1" id="project" name="project"></textarea></td>\
                <td><textarea class="form-control" rows="1" id="content" name="content"></textarea></td>\
                <td>\
                    <select class="form-control" id="type" name="type">\
                        <option>计划任务</option>\
                        <option>临时任务</option>\
                    </select>\
                </td>\
                <td>\
                    <input size="16" readonly type="text" class="form-control weekly-yyyymmdd-add" id="startdate" name="startdate">\
                </td>\
                <td>\
                    <input size="16" readonly type="text" class="form-control weekly-yyyymmdd-add" id="enddate" name="enddate">\
                </td>\
                <td>\
                    <input type="number" class="form-control" id="amount" name="amount">\
                </td>\
                <td><textarea class="form-control" rows="1" id="achievement" name="achievement"></textarea></td>\
            </tr>';
        $("#insertP1").before(html);
    } else if (type == 'unfinished') {
        var html = '\
            <tr class="unfinished">\
                <td><textarea class="form-control" rows="1" id="project" name="project"></textarea></td>\
                <td colspan="2"><textarea class="form-control" rows="1" id="content" name="content"></textarea></td>\
                <td><textarea class="form-control" rows="1" id="actual" name="actual"></textarea></td>\
                <td><textarea class="form-control" rows="1" id="reason" name="reason"></textarea></td>\
                <td>\
                    <input size="16" readonly type="text" class="form-control weekly-yyyymmdd-add" id="plandate" name="plandate">\
                </td>\
                <td><textarea class="form-control" rows="1" id="support" name="support"></textarea></td>\
            </tr>';
        $("#insertP2").before(html);
    } else if (type == 'plan') {
        var html = '\
            <tr class="plan">\
                <td><textarea class="form-control" rows="1" id="project" name="project"></textarea></td>\
                <td colspan="2"><textarea class="form-control" rows="1" id="content" name="content"></textarea></td>\
                <td>\
                    <input size="16" readonly type="text" class="form-control weekly-yyyymmdd-add" id="startdate" name="startdate">\
                </td>\
                <td>\
                    <input size="16" readonly type="text" class="form-control weekly-yyyymmdd-add" id="enddate" name="enddate">\
                </td>\
                <td>\
                    <input type="number" class="form-control" id="amount" name="amount">\
                </td>\
                <td><textarea class="form-control" rows="1" id="achievement" name="achievement"></textarea></td>\
            </tr>';
        $("#insertP3").before(html);
    }
    setupDatePicker('weekly-yyyymmdd-add', 'yyyy-mm-dd');
    $('.weekly-yyyymmdd-add').removeClass('weekly-yyyymmdd-add').addClass('weekly-yyyymmdd');
}

function getItems(cls) {
    var items = [];
    $("."+cls).each(function(idx, root) {
        root.id = 'weekly-id';
        var item = {};
        $("#"+root.id+" :input").each(function(idx, elem) {
            if (elem.name != undefined && elem.name.length > 0) {
                var value = "";
                if (elem != undefined && elem.value.length > 0) {
                    value = elem.value;
                }
                item[elem.name] = elem.value;
            }
        });
        root.id = '';
        items.push(item);
    });
    return items;
}

function getReqObj() {
    var date = $("#date").val();
    var num = $("#num").val();
    var current_start = $("#current_start").val();
    var current_end = $("#current_end").val();
    var next_start = $("#next_start").val();
    var next_end = $("#next_end").val();

    var finished_items = getItems("finished");
    var unfinished_items = getItems("unfinished");
    var plan_items = getItems("plan");

    var req_obj = {};
    req_obj['date'] = date;
    req_obj['num'] = num;
    req_obj['current_start'] = current_start;
    req_obj['current_end'] = current_end;
    req_obj['next_start'] = next_start;
    req_obj['next_end'] = next_end;
    req_obj['finished'] = finished_items;
    req_obj['unfinished'] = unfinished_items;
    req_obj['plan'] = plan_items

    return req_obj;
}

$(document).ready(function() {
    setupDatePicker('weekly-yyyymm', 'yyyy-mm');
    setupDatePicker('weekly-yyyymmdd', 'yyyy-mm-dd');
    $("#insertBtn1").click(function() {insertItem('finished')});
    $("#insertBtn2").click(function() {insertItem('unfinished')});
    $("#insertBtn3").click(function() {insertItem('plan')});

    $("#add").click(function() {
        $.ajax({
            type: 'POST',
            url: '/add',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(getReqObj()),
            success: function(data) {
                if (data['ret'] == true) {
                    window.location.href = '/download?filename='+encodeURIComponent(data['filename']);
                } else {
                    alert(data['err']);
                }
            },
            error: function(err) {
                alert(err.message);
            }
        });
    });

    $("#save").click(function() {
        $.ajax({
            type: 'POST',
            url: '/save',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(getReqObj()),
            success: function(data) {
                if (data['ret'] == true) {
                    alert('保存成功');
                } else {
                    alert(data['err']);
                }
            },
            error: function(err) {
                alert(err.message);
            }
        });
    });
});
