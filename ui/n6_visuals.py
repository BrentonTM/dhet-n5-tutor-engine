"""Course and topic routing for N6 interactive study models."""

from ui.industrial_electronics_n6 import MODULES


N6_VISUAL_TOPICS = {
    "mathematics-N6": {
        "Differentiation": ("derivative",),
        "Integration techniques": ("riemann",),
        "Differential equations": ("ode_decay",),
        "Areas and volumes": ("riemann", "revolve"),
        "Centroids and centres of gravity": ("composite_centroid_3d",),
        "Second moments of area, moments of inertia and centres of fluid pressure": ("second_moment",),
    },
    "industrial_electronics-N6": {module.title: module.models for module in MODULES},
    "digital_electronics-N6": {
        "Combinational logic and code conversion": ("logic_gate_board", "full_adder_3d", "kmap4"),
        "Counters and clock signals": ("ripple_counter_3d",),
        "Digital and analogue conversion": ("flash_adc_3d", "weighted_dac_3d"),
    },
    "industrial_instruments-N6": {
        "Automatic control and step response": ("pid_loop", "step_response"),
        "Level measurement and signal transmission": ("tank_level", "current_loop_3d"),
    },
    "electrotechnics-N6": {
        "Transformers": ("transformer_turns_3d",),
        "AC theory": ("phasor",),
        "DC machines": ("h_bridge_3d",),
    },
    "power_machines-N6": {
        "Internal combustion engines": ("four_stroke_3d",),
        "Steam turbines": ("turbine_stage_3d",),
    },
    "strength_of_materials_structures-N6": {
        "Beam bending and deflection": ("beam_point_load_3d",),
        "Section geometry refresher": ("second_moment", "composite_centroid_3d"),
    },
    "mechanical_drawing_design-N6": {
        "Spur gears and gear drives": ("gear_pair_3d",),
        "Section geometry refresher": ("second_moment",),
    },
    "building_structural_construction-N6": {
        "Concrete beam loading": ("beam_point_load_3d",),
        "Steel section geometry": ("composite_centroid_3d", "second_moment"),
    },
    "building_structural_surveying-N6": {
        "Angular measurement and levelling": ("survey_sight_3d",),
    },
    "chemical_plant_operation-N6": {
        "Material balance across a mixing vessel": ("process_mixer_3d",),
        "Tank level measurement and control": ("tank_level", "pid_loop"),
    },
    "chemical_technology-N6": {
        "Solution concentration and material balance": ("process_mixer_3d",),
        "Acidity and pH measurement": ("ph_probe",),
    },
}


N6_LAB_MODELS = {
    course: tuple(dict.fromkeys(model for models in topics.values() for model in models))
    for course, topics in N6_VISUAL_TOPICS.items()
}


N6_FORMULA_CARDS = {
    "mathematics-N6": ("Composite centroid", "x̄ = Σ(Aᵢxᵢ) / ΣAᵢ",
                        [("Aᵢ", "part area"), ("xᵢ", "part centroid")], "Use a common origin for every part."),
    "digital_electronics-N6": ("Binary-weighted output", "Value = 8b₃ + 4b₂ + 2b₁ + b₀",
                              [("bᵢ", "bit state")], "Each bit position contributes twice the weight of the one below it."),
    "industrial_instruments-N6": ("Current loop span", "I = 4 + 16f",
                                  [("I", "current in mA"), ("f", "fraction of span")], "A healthy 4–20 mA loop reads 4 mA at the lower range value."),
    "electrotechnics-N6": ("Ideal transformer ratio", "Vₛ/Vₚ = Nₛ/Nₚ",
                          [("V", "RMS voltage"), ("N", "turns")], "Compare the primary and secondary windings before deciding whether voltage steps up or down."),
    "power_machines-N6": ("Turbine shaft power", "P ≈ ṁ Δh",
                          [("ṁ", "steam mass flow"), ("Δh", "actual enthalpy drop")], "Use kg/s and kJ/kg to obtain kW."),
    "strength_of_materials_structures-N6": ("Support equilibrium", "Rₐ + Rᵦ = P",
                                           [("Rₐ, Rᵦ", "support reactions"), ("P", "downward point load")], "Use moments about one support to find the other reaction."),
    "mechanical_drawing_design-N6": ("External gear speed", "n₂/n₁ = −z₁/z₂",
                                    [("n", "signed shaft speed"), ("z", "tooth count")], "The minus sign indicates opposite rotation."),
    "building_structural_construction-N6": ("Moment under a point load", "M = Rₐa",
                                           [("Rₐ", "left reaction"), ("a", "load distance from left support")], "Take moments on the left segment up to the load."),
    "building_structural_surveying-N6": ("Sight line rise", "Δh = d tan θ",
                                        [("d", "horizontal distance"), ("θ", "signed vertical angle")], "Add instrument height and subtract target height to compare the stations."),
    "chemical_plant_operation-N6": ("Steady mixing balance", "ṁₒᵤₜ = ṁₐ + ṁᵦ",
                                    [("ṁ", "mass flow")], "At steady state, total mass entering equals total mass leaving."),
    "chemical_technology-N6": ("Mixture mass fraction", "w = mₛ/m",
                               [("mₛ", "solute mass"), ("m", "total solution mass")], "Multiply the mass fraction by 100 for mass percent."),
}
