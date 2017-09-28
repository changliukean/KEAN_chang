/**
 * 分页函数
 * pno--页数
 * psize--每页显示记录数
 * 分页部分是从真实数据行开始，因而存在加减某个常数，以确定真正的记录数
 * 纯js分页实质是数据行全部加载，通过是否显示属性完成分页功能
 **/
function go_page(pno,psize){
    var itable = document.getElementById("preview_tbody");
    var num = itable.rows.length;//表格所有行数(所有记录数)
    var totalPage = 0;//总页数
    var pageSize = psize;//每页显示行数
    //总共分几页
    if(num/pageSize > parseInt(num/pageSize)){
            totalPage=parseInt(num/pageSize)+1;
       }else{
           totalPage=parseInt(num/pageSize);
       }
    var currentPage = pno;//当前页数
    var startRow = (currentPage - 1) * pageSize+1;//开始显示的行  31
       var endRow = currentPage * pageSize;//结束显示的行   40
       endRow = (endRow > num)? num : endRow;    40
       //遍历显示数据实现分页
    for(var i=1;i<(num+1);i++){
        var irow = itable.rows[i-1];
        if(i>=startRow && i<=endRow){
            irow.style.display = "table-row";
        }else{
            irow.style.display = "none";
        }
    }
    return num;
}


function paging(){
  go_page($(".pagination").pagination('getCurrentPage'),24);
  // alert($(".pagination").pagination('getCurrentPage'));
  $(".pagination").pagination('selectPage',$(".pagination").pagination('getCurrentPage'));

}



function upload_lmp_to_kean(lmp_result_list){


  if(lmp_result_list){
    var user_confirm = confirm("Are you sure to upload "+lmp_result_list.length+" records of data to KEAN?");
    if(user_confirm){
      // for(var i = 0; i<lmp_result_list.length;i++){
      //   lmp_result_list[i] = String(lmp_result_list[i]);
      // }
      document.getElementById("lmp_upload").innerHTML = 'UPLOADING';
      document.getElementById("lmp_upload").disabled = true;
      $.ajax({
        url: '/sys_mainpage/upload_pjmlmp_to_kean/',
        type: 'post',
        dataType:'json',
        data:{'lmp_result_list': JSON.stringify(lmp_result_list)},
        success: function(data) {
          document.getElementById("lmp_upload").innerHTML = 'UPLOAD TO KEAN';
          document.getElementById("lmp_upload").disabled = false;
          alert("LMP data successfully uploaded to KEAN.");
          $("#latest_lmp_info_tbody").empty();
          latest_lmp_info_list = data['latest_lmp_info_list'];
          var add_row_str = '';
          for(var i=0;i<latest_lmp_info_list.length;i++){
            add_row_str = add_row_str + "<tr>";
              for(var j=0;j<latest_lmp_info_list[i].length;j++){
                add_row_str = add_row_str +"<td>"+latest_lmp_info_list[i][j]+"</td>";
              }
            add_row_str = add_row_str + "</tr>";
          }
          $("#latest_lmp_info_tbody").append(add_row_str);
        },
        failure: function(data) {
            alert('Got an error dude');
        }
      });
    }
  }else{
    alert("No data to upload.");
  }

}


function check_financials_status(){
    var selected_com_scen = document.getElementById("company_scenario").value;

    $("#fsli_status").empty();
    $("#input_data_status").empty();

    $("#version_picker").find("option").remove();
    $("#version_picker").append('<option value="">Please select a version</option>');

    $.ajax({
      url: '/sys_mainpage/check_financials_status/'+selected_com_scen+'/',
      type: 'get',
      dataType:'json',
      success: function(data) {
        document.getElementById("selected_company_scenario").innerHTML = data.selected_company_scenario;
        document.getElementById("selected_company_scenario_input").innerHTML = data.selected_company_scenario + " Input Status";
        document.getElementById("version_picker").disabled = false;
        document.getElementById("check_version").disabled = false;
        document.getElementById("actuals_period").innerHTML = data.actuals_period;
        document.getElementById("estimate_period").innerHTML = data.estimate_period;
        document.getElementById("forecast_period").innerHTML = data.forecast_period;
        var version_list = data.version_list;
        var input_status_list = data.input_status_list;
        for (var i=0;i<version_list.length;i++){
          var temp_version = version_list[i];
          $("#version_picker").append("<option id=" + temp_version + "_" + i + " value=" + temp_version + ">"+temp_version+"</option>");
        }

        for (var i=0;i<input_status_list.length;i++){
          var temp_status = input_status_list[i];
          $("#input_data_status").append("<tr><td>" + temp_status[0] + "</td><td>" + temp_status[1] + "</td><td>" + temp_status[2] + "</td><td>" + temp_status[3] + "</td></tr>");
        }


        $("#liquidity_version_picker").empty();

        for (var i=0;i<version_list.length;i++){
          var temp_version = version_list[i];
          $("#liquidity_version_picker").append("<option id='" + temp_version + "_" + i + "' value='" + temp_version + "'>"+temp_version+"</option>");
        }



      },
      failure: function(data) {
          alert('Got an error dude');
      }
    });
}


function check_version(){
  $("#fsli_status").empty();

  var version = $("#version_picker").val();
  console.log(version);
  if(version == ''){
    alert("Please select a version");
  }
  else
  {
    var selected_company_scenario = $("#company_scenario").val();
    console.log(selected_company_scenario);
    var selected_version = $("#version_picker").val();
    $.ajax({
      url: '/sys_mainpage/check_version_status/'+selected_company_scenario+"/"+selected_version+'/',
      type: 'get',
      dataType:'json',
      success: function(data) {
        var fsli_status_list = data.fsli_status_list;
        var fsli_status_tbody = $("#fsli_status");
        for(var i = 0; i<fsli_status_list.length;i++){
            var temp_row = fsli_status_list[i];
            fsli_status_tbody.append("<tr><td>" + temp_row[0] + "</td><td>" + temp_row[1] + "</td><td>" + temp_row[2] + "</td><td>" + temp_row[3] + "</td><td>" + temp_row[4] + "</td><td>" + temp_row[5] + "</td></tr>");
        }
      },
      failure: function(data) {
          alert('Got an error dude');
      }
    });

  }

}


function pick_yesterday_date(){
    var $today = new Date();
    var $yesterday = new Date($today);
    $yesterday.setDate($today.getDate() - 1);
    var $dd = $yesterday.getDate();
    var $mm = $yesterday.getMonth()+1; //January is 0!
    var $yyyy = $yesterday.getFullYear();

    if($dd<10){$dd='0'+$dd}
    if($mm<10){$mm='0'+$mm}
    $yesterday = $yyyy+'-'+$mm+'-'+$dd;
    document.getElementById("start_date").value = $yesterday;
    document.getElementById("end_date").value = $yesterday;

}


function initiate_amr(){
  var selected_company = $("#company_picker").val();
  var selected_month = $("#month_picker").val();
  var current_year = (new Date()).getFullYear();

  var user_confirm = confirm("Are you sure to initiate AMR: "+selected_company +"-"+current_year+" "+selected_month+" AMR ?");

  if(user_confirm){

          $.ajax(
            {
              url: "/sys_mainpage/initiate_amr/"+selected_company +"-"+current_year+" "+selected_month+" AMR"+"/",
              type: 'get',
              success: function(data){
                $("#company_scenario").append("<option selected = 'selected' value='" + selected_company + "-" + current_year + " " + selected_month + " AMR'" + ">" + selected_company + "-" + current_year + " " + selected_month+" AMR" + "</option>");
              },

              failure: function(data){
                alert("got an error");
              }


            }
          );
  }else{

    return;
  }

}

function check_upload_file(){
  if($("#exampleInputFile").val() !=""){
    var selected_com_scen = $("#company_scenario").val();
    $("<input />").attr('type','hidden').attr('name','com_scen_picker_upload').attr('value',selected_com_scen).appendTo('#upload_file_form');


    return true;
  }else{
    alert("Please select a file to upload.");
    return false;
  }

}


function run_budget(){
  var budget_status = $("#status_count").html();

  var user_confirm = true;

  if(budget_status > 0){
    user_confirm = confirm("Budget values existing for this AMR, are you sure to rerun budget module? ");
  }

  if(user_confirm){

  selected_company_scenario = $("#company_scenario").val();
  selected_budget = $("#latest_budget_scenario_list").val();

  $.ajax(
          {
          url: "/sys_mainpage/run_budget/selected_com_scen=" + selected_company_scenario + "&budget_scenario=" + selected_budget,
          type: "get",
          dataType: "json",
          success: function(data){
            // console.log(">>>>>>>>>>???");
            // alert("ye!");
            $("#company_scenario").val(data.selected_company_scenario);
            $("#latest_budget_scenario_list").val(data.budget_scenario);
            // alert(data.status_count);
            $("#status_count").html(data.status_count);
          },

          failure: function(data){
            // alert("ha!");
          }

        });

      }else{

        return;
      }

}


function run_budget_for_forecast_period(){
  var budget_status = $("#status_count").html();

  var user_confirm = true;

  if(budget_status > 0){
    user_confirm = confirm("Budget values existing for this AMR, are you sure to rerun budget module? ");
  }

  if(user_confirm){

  selected_company_scenario = $("#company_scenario").val();
  selected_budget = $("#latest_budget_scenario_list").val();

  $.ajax(
          {
          url: "/sys_mainpage/run_budget_for_forecast_period/selected_com_scen=" + selected_company_scenario + "&budget_scenario=" + selected_budget,
          type: "get",
          dataType: "json",
          success: function(data){
            // console.log(">>>>>>>>>>???");
            // alert("ye!");
            $("#company_scenario").val(data.selected_company_scenario);
            $("#latest_budget_scenario_list").val(data.budget_scenario);
            // alert(data.status_count);
            $("#status_count").html(data.status_count);
          },

          failure: function(data){
            // alert("ha!");
          }

        });

      }else{

        return;
      }

}


function submit_amr_run_selection(){
    var amr_run_selection_dom = $("#amr_selection_div input[name='amr_switch[]']:checked");
    // var amr_uselastvf_selection_dom = $("#amr_selection_div input[name='amr_version_switch[]']:checked");


    var selected_company_scenario = $("#company_scenario").val();

    var selected_budget_scenario = $("#latest_budget_scenario_list").val();


    var amr_run_selection_list = [];
    var amr_uselastvf_selection_list = [];

    amr_run_selection_dom.each(function(i,obj){
        amr_run_selection_list.push(obj.value);
    });


    // amr_uselastvf_selection_dom.each(function(i,obj){
    //     amr_uselastvf_selection_list.push(obj.value);
    // });




    $("#amr_run_selection_submit").html("Processing...");
    $("#amr_run_selection_submit").attr("disabled","disabled");

    $.ajax(
      {
        url:"/sys_mainpage/run_amr",
        type:"post",
        dataType:"json",
        data: {"amr_run_selection_list":JSON.stringify(amr_run_selection_list),"selected_com_scen":selected_company_scenario, "budget_scenario":selected_budget_scenario},
        success: function(response){
          $("#amr_run_selection_submit").html("Run AMR");
          $("#amr_run_selection_submit").prop("disabled",false);
          alert("Selected modules processed.");
        },

        failure: function(response){
          alert("something run with amr logic.");

        }
      }
    );



}


function initiate_report_panels(){
    var selected_com_scen = $("#company_scenario").val();

    $.ajax(
      {
          url:"/sys_mainpage/initiate_amr_report/selected_com_scen=" +selected_com_scen,
          dataType:"json",
          type:"get",
          success: function(data){
              var version_list = data.version_list;

              $("#amr_version_picker").empty();

              for (var i=0;i<version_list.length;i++){
                var temp_version = version_list[i];
                $("#amr_version_picker").append("<option id='" + temp_version + "_" + i + "' value='" + temp_version + "'>"+temp_version+"</option>");
              }


              $("#budget_scenario_picker").empty();

              var latest_budget_scenario_list = data.latest_budget_scenario_list;
              for (var i=0;i<latest_budget_scenario_list.length;i++){
                var temp_version = latest_budget_scenario_list[i];
                $("#budget_scenario_picker").append("<option id='" + temp_version + "_" + i + "' value='" + temp_version + "'>"+temp_version+"</option>");
              }

              $("#version_year_picker").empty();

              var version_year_list = data.version_year_list;
              for (var i=0;i<version_year_list.length;i++){
                var temp = version_year_list[i];
                $("#version_year_picker").append("<option id='" + temp + "_" + i + "' value='" + temp + "'>"+temp+"</option>");
              }


          },

          failure: function(data){


          },
      }
    );



}



function generate_amr_report(){
    var selected_com_scen = $("#company_scenario").val();
    var budget_scenario = $("#budget_scenario_picker").val();
    var amr_version = $("#amr_version_picker").val();
    $.ajax(
      {
          url:"/sys_mainpage/generate_amr_report/selected_com_scen=" + selected_com_scen + "&amr_version=" + amr_version + "&budget_scenario=" + budget_scenario,
          dataType:"json",
          type:"get",
          success: function(response){
            file_path = response.file_path;
            // alert(file_path);
            var current_href = "/sys_mainpage/download_amr_report/file_path=";
            // alert(current_href);
            $("#download_amr_report").attr("href", current_href + file_path);
            $("#download_amr_report")[0].click();

          },

          failure: function(response){


          },
      }
    );

}



function generate_fy_report(){
    var selected_com_scen = $("#company_scenario").val();
    var version_year = $("#version_year_picker").val();

    $.ajax(
      {
          url:"/sys_mainpage/generate_fy_report/selected_com_scen=" + selected_com_scen + "&version_year=" + version_year,
          dataType:"json",
          type:"get",
          success: function(response){
            file_path = response.file_path;
            // alert(file_path);
            var current_href = "/sys_mainpage/download_amr_report/file_path=";
            // alert(current_href);
            $("#download_amr_report").attr("href", current_href + file_path);
            $("#download_amr_report")[0].click();

          },

          failure: function(response){


          },
      }
    );

}



function check_all_scenario_version(){
    var selected_company = $("#company_picker").val();

    $.ajax(
      {
          url:"/sys_mainpage/check_company_status/selected_company=" + selected_company,
          dataType:"json",
          type:"get",
          success: function(response){
            var company_status_list = response.company_status_list;
            $("#scenario_version_year_picker_1").empty();

            for (var i=0;i<company_status_list.length;i++){
              var temp = company_status_list[i];
              $("#scenario_version_year_picker_1").append("<option id='" + temp + "_" + i + "' value='" + temp + "'>"+temp+"</option>");
            }


            $("#scenario_version_year_picker_2").empty();

            for (var i=0;i<company_status_list.length;i++){
              var temp = company_status_list[i];
              $("#scenario_version_year_picker_2").append("<option id='" + temp + "_" + i + "' value='" + temp + "'>"+temp+"</option>");
            }


          },

          failure: function(response){


          },
      }
    );

}


function generate_variance_report(){
    var selected_com_scen = $("#company_scenario").val();
    var budget_scenario = $("#budget_scenario_picker").val();
    var amr_version = $("#amr_version_picker").val();
    $.ajax(
      {
          url:"/sys_mainpage/generate_variance_report/selected_com_scen=" + selected_com_scen + "&amr_version=" + amr_version + "&budget_scenario=" + budget_scenario,
          dataType:"json",
          type:"get",
          success: function(response){
            file_path_ytd = response.file_path_ytd;
            // alert(file_path);
            var current_href = "/sys_mainpage/download_amr_report/file_path=";
            // alert(current_href);
            $("#download_amr_report").attr("href", current_href + file_path_ytd);
            window.open($("#download_amr_report").attr("href"));

            file_path_mtd = response.file_path_mtd;
            // alert(file_path);
            var current_href = "/sys_mainpage/download_amr_report/file_path=";
            // alert(current_href);
            $("#download_amr_report_1").attr("href", current_href + file_path_mtd);
            // $("#download_amr_report_1")[0].click();
            window.open($("#download_amr_report_1").attr("href"));

          },

          failure: function(response){


          },
      }
    );


}



function compare_diff_report(){

    var selected_company = $("#company_picker").val();
    var first_scenario_version_year = $("#scenario_version_year_picker_1").val();
    var second_scenario_version_year = $("#scenario_version_year_picker_2").val();

    $.ajax(
      {
          url:"/sys_mainpage/generate_diff_report/first_svy=" + first_scenario_version_year + "&second_svy=" + second_scenario_version_year + "&selected_company=" + selected_company,
          dataType:"json",
          type:"get",
          success: function(response){
            file_path = response.file_path;
            // alert(file_path);
            var current_href = "/sys_mainpage/download_amr_report/file_path=";
            // alert(current_href);
            $("#download_amr_report").attr("href", current_href + file_path);
            $("#download_amr_report")[0].click();

          },

          failure: function(response){


          },
      }
    );

}


function run_liquidity(){
  var selected_com_scen = $("#company_scenario").val();
  var amr_version = $("#liquidity_version_picker").val();

  $.ajax({
    url: "/sys_mainpage/run_liquidity/selected_com_scen=" + selected_com_scen + "&amr_version=" + amr_version,
    dataType: 'json',
    type:'get',
    success: function(response){
              var liquidity_file_path = response.liquidity_file_path;
              var debt_balance_file_path = response.debt_balance_file_path;
              var interest_expense_file_path = response.interest_expense_file_path;
              var est_tax_dist_file_path = response.est_tax_dist_file_path;

              var current_href = "/sys_mainpage/download_amr_report/file_path=";

              $("#download_report").attr("href", current_href + liquidity_file_path);
              window.open($("#download_report").attr("href"));

              $("#download_report_1").attr("href", current_href + debt_balance_file_path);
              window.open($("#download_report_1").attr("href"));

              $("#download_report_2").attr("href", current_href + interest_expense_file_path);
              window.open($("#download_report_2").attr("href"));

              $("#download_report_3").attr("href", current_href + est_tax_dist_file_path);
              window.open($("#download_report_3").attr("href"));


            },
    failure: function(response){


            },

  });

}


function make_version(){
    var input_version = $("#input_version").val();

    if(input_version == ''){
        input_version = 'Current';
    }
    var selected_com_scen = $("#company_scenario").val();

    $.ajax({
      url: "/sys_mainpage/make_version/selected_com_scen=" + selected_com_scen + "&input_version=" + input_version,
      dataType: 'json',
      type:'get',
      success: function(response){},
      failure: function(response){},

    });

}


function run_pxq(){
    var selected_com_scen = $("#company_scenario").val();
    var amr_version = $("#liquidity_version_picker").val();
    var budget_scenario = $("#latest_budget_scenario_list_for_support").val();

    $.ajax({
      url: "/sys_mainpage/run_pxq/selected_com_scen=" + selected_com_scen + "&amr_version=" + amr_version + "&budget_scenario=" + budget_scenario,
      dataType: 'json',
      type:'get',
      success: function(response){
        file_path = response.file_path;
        var current_href = "/sys_mainpage/download_amr_report/file_path=";
        $("#download_report").attr("href", current_href + file_path);
        $("#download_report")[0].click();
      },
      failure: function(response){},

    });
}



function copy_from_selected(){

    var current_com_scen = $("#company_scenario").val();
    var selected_com_scen = $("#company_scenario_copy").val();
    var selected_fsli = $("#fsli").val();
    var selected_module = $("#module_picker").val();

    $.ajax({
      url: "/sys_mainpage/copy_from_selected/current_com_scen=" + current_com_scen + "&selected_com_scen=" + selected_com_scen + "&fsli=" + selected_fsli + "&module=" + selected_module,
      dataType: 'json',
      type:'get',
      success: function(response){

      },
      failure: function(response){},

    });


}


function plot_bvr(){
    var selected_com_scen = $("#company_scenario_picker").val();
    var selected_entity = $("#entity_picker").val();
    var selected_fsli = $("#fsli").val();


    $.ajax({
      url: "/sys_mainpage/plot_bvr/selected_com_scen=" + selected_com_scen + "&selected_entity=" + selected_entity + "&selected_fsli=" + selected_fsli,
      dataType: 'json',
      type:'get',
      success: function(response){

        $('#bvr_plot_div').css('visibility', 'visible');

        var af_value_list = response.af_value_list;

        var budget_value_list = response.budget_value_list;

        console.log();(af_value_list.length);
        console.log();(budget_value_list.length);

        var af_value_array = [];
        var budget_value_array = [];


        for(var i=0;i<af_value_list.length;i++){
            af_value_array.push({y:af_value_list[i][2], label:af_value_list[i][3]});
        }

        for(var i=0;i<budget_value_list.length;i++){
            budget_value_array.push({y:budget_value_list[i][2], label:budget_value_list[i][3]});
        }



        var selected_entity = response.selected_entity;
        var selected_fsli = response.selected_fsli;

        console.log(selected_entity);
        console.log(selected_fsli);

        console.log(af_value_array);
        console.log(budget_value_array);


        var chart = new CanvasJS.Chart("bvr_plot_div",
            {
              theme: "theme3",
                                animationEnabled: true,
              title:{
                text: selected_entity + " " + selected_fsli,
                fontSize: 30
              },
              toolTip: {
                shared: true
              },

              data: [
              {
                type: "column",
                name: "A+F ($000)",
                legendText: selected_fsli + " A+F",
                showInLegend: true,
                dataPoints:af_value_array,
              },
              {
                type: "column",
                name: "Budget ($000)",
                legendText: selected_fsli + " Budget",
                // axisYType: "secondary",
                showInLegend: true,
                dataPoints:budget_value_array
              }

              ],
                  legend:{
                    cursor:"pointer",
                    itemclick: function(e){
                      if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                        e.dataSeries.visible = false;
                      }
                      else {
                        e.dataSeries.visible = true;
                      }
                      chart.render();
                    }
                  },
                });

        chart.render();

      },
      failure: function(response){},

    });




}
