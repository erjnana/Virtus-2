import openmdao.api as om
from stability import *

np=1
proc_case=[]

if (np > 1):
    for p in range(np):

        crp= om.CaseReader('./log/evolutions/banana_2026_02_02_1917.db'+str(p))
        driver_cases = crp.list_cases('driver')
        cases = crp.get_cases()
        proc_case.append(cases)

else:
    crp= om.CaseReader('./log/evolutions/banana_2026_02_02_1917.db')
    driver_cases = crp.list_cases('driver')
    cases = crp.get_cases()
    proc_case.append(cases)

for proc_n in range(len(proc_case)):

    proc_case[proc_n]= proc_case[proc_n][-19900:]


    for case in proc_case[proc_n]:

        if (
            #True
            (case.outputs['individual_scorer.a_trim'] <= a_trim_max)
            and (case.outputs['individual_scorer.a_trim'] >= a_trim_min)
            and (case.outputs['individual_scorer.x_cg_p'] <=0.40) 
            and (case.outputs['individual_scorer.x_cg_p'] >= 0.25) 
            and (case.outputs['individual_scorer.me'] <= me_max)
            and (case.outputs['individual_scorer.me'] >= me_min)
            #and (case.outputs['individual_scorer.ar'] >= 5)
            #and (case.outputs['individual_scorer.vht'] <= 0.8)
            and (case.outputs['individual_scorer.vvt'] >= vvt_min)
            and (case.outputs['individual_scorer.cp'] >= 12.900)
            #and (case.outputs['individual_scorer.g_const'] <= 2.9)
            #and (case.outputs['individual_scorer.g_const'] >= 2.8)
            ):

            print('-------------- PROTOTIPO:', case.name[-4:]+'-'+str(proc_n)+' --------------\n')
            print(
                ' Variaveis de design: (',
                  ' w_bt= ',float(case.outputs['w_bt']),','
                  ' w_baf= ',float(case.outputs['w_baf']),','
                  ' w_cr= ',float(case.outputs['w_cr']),','
                  ' w_ci= ',float(case.outputs['w_ci']),','
                  ' w_ct= ',float(case.outputs['w_ct']),','
                  ' w_z= ',float(case.outputs['w_z']),','
                  ' w_inc= ',float(case.outputs['w_inc']),','
                  ' w_wo= ',float(case.outputs['w_wo']),','
                  ' w_d= ',float(case.outputs['w_d']),','
                  ' eh_b= ',float(case.outputs['eh_b']),','
                  ' eh_cr= ',float(case.outputs['eh_cr']),','
                  ' eh_ct= ',float(case.outputs['eh_ct']),','
                  ' eh_inc= ',float(case.outputs['eh_inc']),','
                  ' ev_b= ',float(case.outputs['ev_b']),','
                  ' ev_ct= ',float(case.outputs['ev_ct']),','
                  ' eh_x= ',float(case.outputs['eh_x']),','
                  ' eh_z= ',float(case.outputs['eh_z']),','
                  ' motor_x= ',float(case.outputs['motor_x']),','
                  #'pot= ',float(case.outputs['pot']),','
                  ')'
                  , sep=''
                  )
            
            print(
                '\n Objetivos\n',
                  '     Carga paga=', float(case.outputs['individual_scorer.score'])
                  )
            
            print(
                '\n Restricoes\n',
                  #'     Altura=', float(case.outputs['individual_scorer.h_const']),'\n',
                  '     Gap do EH=', float(case.outputs['individual_scorer.eh_z_const']),'\n',
                  '     Gap do CG=', float(case.outputs['individual_scorer.low_cg']),'\n',
                  '     VHT=', float(case.outputs['individual_scorer.vht']),'\n',
                  '     VVT=', float(case.outputs['individual_scorer.vvt']),'\n',
                  '     AR=', float(case.outputs['individual_scorer.ar']),'\n',
                  '     AR do EH=', float(case.outputs['individual_scorer.eh_ar']),'\n',
                  #'     Cm0=', float(case.outputs['individual_scorer.cm0']),'\n',
                  '     CG em=', float(case.outputs['individual_scorer.x_cg_p']),'\n',
                  '     Angulo de trimagem=', float(case.outputs['individual_scorer.a_trim']),'\n',
                  '     Margem Estatica=', float(case.outputs['individual_scorer.me']),'\n'
                  )