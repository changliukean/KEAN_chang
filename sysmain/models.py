from django.db import models

# Create your models here.


class financials(models.Model):
    class Meta:
        db_table = 'financials';

    id_financials = models.IntegerField(primary_key=True);
    company = models.CharField(max_length=50);
    entity = models.CharField(max_length=100);
    scenario = models.CharField(max_length=50);
    account = models.CharField(max_length=100);
    period = models.DateField();
    value = models.FloatField(max_length=25);

class company_scenario(models.Model):
    class Meta:
        db_table = 'company_scenario';

    id_company_scenario = models.IntegerField(primary_key=True);
    company = models.CharField(max_length=50);
    scenario = models.CharField(max_length=50);


class power_plants(models.Model):
    id_power_plants = models.IntegerField(primary_key=True);
    company = models.CharField(max_length=50);
    power_plant_name = models.CharField(max_length=50);
    unit = models.CharField(max_length=50);
    pnode_id = models.CharField(max_length=45);
    ucap = models.IntegerField();
    p_type = models.CharField(max_length=25);
    fuel = models.CharField(max_length=25);
    heat_rate = models.FloatField(max_length=25);
    fuel_instrument_id = models.CharField(max_length=15);


class lmp(models.Model):
    class Meta:
        db_table = 'lmp';
    valuation_date = models.DateField();
    pnode_id = models.CharField(max_length=45);
    dart = models.CharField(max_length=45);
    hour_ending = models.CharField(max_length=5);
    total_lmp = models.FloatField(max_length=25);
    congestion_price = models.FloatField(max_length=25);
    marginal_loss_price = models.FloatField(max_length=25);




class actuals(models.Model):
    class Meta:
        db_table = 'actuals';

    id_actuals = models.IntegerField(primary_key=True);
    accounting_month = models.DateField();
    as_of_date = models.DateField();
    report_date = models.DateField();
    scenario = models.CharField(max_length = 50);
    company = models.CharField(max_length = 50);
    entity = models.CharField(max_length = 50);
    plant_id = models.CharField(max_length = 50);
    business_unit_id = models.CharField(max_length = 10);
    account = models.CharField(max_length = 50);
    account_title = models.CharField(max_length = 100);
    bvr_group = models.CharField(max_length = 50);
    project_id = models.CharField(max_length = 50);
    project_name = models.CharField(max_length = 50);
    period_balance = models.FloatField(max_length=25);
    ending_balance = models.FloatField(max_length=25);
    total_credit = models.FloatField(max_length=25);
    total_debit = models.FloatField(max_length=25);
    reference_number = models.CharField(max_length=50);
    contract_number = models.CharField(max_length=20);
    invoice_id = models.CharField(max_length=50);
    outage_code = models.CharField(max_length=10);
    work_order_number = models.CharField(max_length=50)
    cost_component = models.CharField(max_length=50)



class budget(models.Model):
    class Meta:
        db_table = 'budget';

    id_budget = models.IntegerField(primary_key=True);
    company = models.CharField(max_length = 50);
    scenario = models.CharField(max_length = 50);
    entity = models.CharField(max_length = 50);
    account = models.CharField(max_length = 50);
    account_name = models.CharField(max_length = 100);
    period = models.DateField();
    value = models.FloatField(max_length=25);
    model_group = models.CharField(max_length = 50);
    project_id = models.CharField(max_length = 500);
    cost_component_id = models.CharField(max_length=50)
    work_order_number = models.CharField(max_length=50)
    outage_code_id = models.CharField(max_length=10);
    invoice_id = models.CharField(max_length=50);
    contract_number_id = models.CharField(max_length=20);
    reference_number = models.CharField(max_length=50);
    cost_category = models.CharField(max_length=50);
    cost_sub_category = models.CharField(max_length=50);
    project_name = models.CharField(max_length = 500);




class dispatch(models.Model):
    class Meta:
        db_table = 'dispatch';
    id_dispatch = models.IntegerField(primary_key=True);
    scenario = models.CharField(max_length = 50);
    company = models.CharField(max_length = 50);
    entity = models.CharField(max_length = 50);
    fsli = models.CharField(max_length = 50);
    period = models.DateField();
    value = models.FloatField(max_length=25);



class project_respread(models.Model):
    class Meta:
        db_table = 'project_respread';
    id_project_respread = models.IntegerField(primary_key=True);
    company = models.CharField(max_length = 50);
    scenario = models.CharField(max_length = 50);
    entity = models.CharField(max_length = 50);
    account = models.CharField(max_length = 50);
    account_name = models.CharField(max_length = 100);
    period = models.DateField();
    value = models.FloatField(max_length=25);

    model_group = models.CharField(max_length=50);

    project_id = models.CharField(max_length = 50);
    project_name = models.CharField(max_length = 50);

    cost_component_id = models.CharField(max_length=50)
    work_order_number = models.CharField(max_length=50)
    outage_code_id = models.CharField(max_length=10);
    invoice_id = models.CharField(max_length=50);
    contract_number_id = models.CharField(max_length=20);
    reference_number = models.CharField(max_length=50);

    cost_category = models.CharField(max_length=50);
    cost_sub_category = models.CharField(max_length=50);

class prices(models.Model):
    class Meta:
        db_table = 'prices';

    id_prices = models.IntegerField(primary_key=True);
    scenario = models.CharField(max_length = 50);
    valuation_date = models.DateField();
    instrument_id = models.CharField(max_length = 200);
    period = models.DateField();
    price = models.FloatField(max_length=25);

class pxq_input(models.Model):
    class Meta:
        db_table = 'pxq_input';
    id_pxq_input = models.IntegerField(primary_key=True);
    scenario = models.CharField(max_length = 50);
    company = models.CharField(max_length = 50);
    entity = models.CharField(max_length = 50);
    data_source = models.CharField(max_length = 10);
    input_title = models.CharField(max_length = 200);
    period = models.DateField();
    value = models.FloatField(max_length=25);
