import pandas as pd;





def provide_project_detail():
    actual_project_df = pd.read_excel('S:/ChangLiu/Github/KEAN_Web/virtual_env/kean_website/sysmain/KEAN_PROJ/scripts/actual_budget_project_dump.xlsx', 'Actual', header = 0);
    print (len(actual_project_df));

    print (actual_project_df.columns);

    budget_project_df = pd.read_excel('S:/ChangLiu/Github/KEAN_Web/virtual_env/kean_website/sysmain/KEAN_PROJ/scripts/actual_budget_project_dump.xlsx', 'Budget', header = 0);
    print (len(budget_project_df));

    print (budget_project_df.columns);




if __name__ == '__main__':
    provide_project_detail();
