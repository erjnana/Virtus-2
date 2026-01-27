class Prototype:
    """
    Constrói a geometria completa da aeronave no AVL.

    Convenções:
    - w_* : asa
    - eh_* : estabilizador horizontal
    - ev_* : estabilizador vertical
    """

    def __init__(
        self,
        # ---------------- ASA ----------------
        w_bt, w_baf, w_cr, w_ci, w_ct,
        w_z, w_inc, w_wo, w_d,

        # ---------------- EH ----------------
        eh_b, eh_cr, eh_ct, eh_inc, eh_x, eh_z,

        # ---------------- EV ----------------
        ev_b, ev_ct,

        # ---------------- MOTOR ----------------
        motor_x, motor_z=0.30,

        # ---------------- PERFIS ----------------
        root_af=None,
        tip_af=None,
        eh_af=None,

        # ---------------- OPÇÕES ----------------
        ge=False
    ):
        # ====================================================
        # CONVERSÃO DE VARIÁVEIS ADIMENSIONAIS
        # ====================================================
        w_ci = w_ci * w_cr
        w_ct = w_ct * w_ci
        w_baf = w_baf * w_bt
        eh_ct = eh_ct * eh_cr

        # ====================================================
        # ARMAZENAMENTO DA ASA
        # ====================================================
        self.w_bt = w_bt
        self.w_baf = w_baf
        self.w_cr = w_cr
        self.w_ci = w_ci
        self.w_ct = w_ct
        self.w_inc = w_inc
        self.w_wo = w_wo
        self.w_z = w_z
        self.w_d = w_d

        # ====================================================
        # EMPENAGEM HORIZONTAL
        # ====================================================
        self.eh_b = eh_b
        self.eh_cr = eh_cr
        self.eh_ct = eh_ct
        self.eh_inc = eh_inc
        self.eh_x = eh_x
        self.eh_z = eh_z

        # ====================================================
        # EMPENAGEM VERTICAL
        # ====================================================
        self.ev_b = ev_b
        self.ev_cr = eh_cr
        self.ev_ct = ev_ct * self.ev_cr
        self.ev_x = eh_x
        self.ev_y = 0
        self.ev_z = eh_z

        # ====================================================
        # MOTOR
        # ====================================================
        self.motor_x = motor_x
        self.motor_z = motor_z

        # ====================================================
        # FUSELAGEM E BOOM
        # ====================================================
        self.fus_h = 0.12 * w_cr
        self.fus_l = max(1.25 * w_cr, 0.5)
        self.fus_z = w_z - self.fus_h / 2
        self.boom_l = l_boom(self.fus_l, eh_x)

        # ====================================================
        # GRANDEZAS DE REFERÊNCIA
        # ====================================================
        self.s_ref = s_ref(w_cr, w_ci, w_baf, w_ct, w_bt)
        self.c_med = c_med(self.s_ref, w_bt)
        self.mac = mac(0, w_bt, w_baf, w_cr, w_ct)
        self.ref_span = ref_span(w_baf, self.mac, w_cr, w_bt)

        self.svt = svt(self.ev_cr, self.ev_ct, ev_b)
        self.sht = sht(eh_b, eh_cr, eh_ct)

        self.ar = ar(w_bt, self.s_ref)
        self.eh_ar = ar(eh_b, self.sht)

        # ====================================================
        # MASSA E CG
        # ====================================================
        self.pv = total_m(
            self.s_ref, self.sht, self.svt,
            self.fus_h, self.fus_l, self.boom_l
        )

        self.x_cg, self.z_cg = cg(
            self.s_ref, self.w_z, self.w_cr,
            self.sht, self.eh_x, self.eh_z, self.eh_cr,
            self.svt, self.ev_x, self.ev_z, self.ev_cr,
            self.fus_z, self.fus_h, self.fus_l,
            self.boom_l, self.motor_x, self.motor_z
        )

        # ====================================================
        # PERFIS – CARREGADOS DO BANCO
        # ====================================================
        self.root_af = load_airfoil(root_af)
        self.tip_af = load_airfoil(tip_af)
        self.eh_af = load_airfoil(eh_af)

        # ====================================================
        # SEÇÕES – ASA
        # ====================================================
        self.w_root_section = Section(
            leading_edge_point=Point(0, 0, w_z),
            chord=w_cr,
            airfoil=FileAirfoil(self.root_af["dat_path"])
        )

        self.w_tip_section = Section(
            leading_edge_point=Point(
                (w_cr - w_ct) / 4,
                w_bt / 2,
                w_z + z_d(w_bt / 2, w_d)
            ),
            chord=w_ct,
            airfoil=FileAirfoil(self.tip_af["dat_path"]),
            angle=w_wo
        )

        self.wing_surface = Surface(
            name="Wing",
            n_chordwise=12,
            n_spanwise=22,
            sections=[self.w_root_section, self.w_tip_section],
            angle=w_inc,
            y_duplicate=0.0
        )

        self.geometry = Geometry(
            name="Prototype",
            reference_area=self.s_ref,
            reference_chord=self.mac,
            reference_span=self.ref_span,
            reference_point=Point(self.x_cg, 0, self.z_cg),
            surfaces=[self.wing_surface]
        )

        # ====================================================
        # ÂNGULO DE ESTOL POR SEÇÃO
        # ====================================================
        self.alpha_stall_wing = min(
            self.root_af["alpha_clmax"],
            self.tip_af["alpha_clmax"]
        )
        self.alpha_stall_eh = self.eh_af["alpha_clmax"]
        self.alpha_stall_ev = self.eh_af["alpha_clmax"]  # EV normalmente não governa

        # ÂNGULO GLOBAL DE ESTOL DO AVIÃO
        self.alpha_stall_aircraft = min(
            self.alpha_stall_wing,
            self.alpha_stall_eh,
            self.alpha_stall_ev
        )

        # ====================================================
        # RESTRIÇÃO GLOBAL DE ESTOL
        # ====================================================
        self.stall_constraint = self.alpha_stall_aircraft - ALPHA_STALL_MIN_DEG

    # ====================================================
    # MÉTODO DE PRINT DA GEOMETRIA E PERFIS
    # ====================================================
    def print_geometry_info(self):
        print("\n--- Perfis escolhidos ---")
        print(f"Root wing profile: {self.root_af['name']}  |  Alpha_CLmax: {self.root_af['alpha_clmax']}°")
        print(f"Tip wing profile: {self.tip_af['name']}  |  Alpha_CLmax: {self.tip_af['alpha_clmax']}°")
        print(f"Elevator profile: {self.eh_af['name']}  |  Alpha_CLmax: {self.eh_af['alpha_clmax']}°")
        print(f"Ângulo de estol global do avião: {self.alpha_stall_aircraft}°")
        print(f"Stall constraint (>=0 é viável): {self.stall_constraint}°")
