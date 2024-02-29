# The val-color(HEX) records for each map type
color_types ={
            # Integer rasters
            'lumap':   ['Assests/lumap_colors.csv',
                        'Assests/lumap_colors_grouped.csv'],
            'lmmap':    'Assests/lm_colors.csv',
            'ammap':    'Assests/ammap_colors.csv',
            'non_ag':   'Assests/non_ag_colors .csv',
            # Float rasters
            'Ag_LU':    'Assests/float_img_colors.csv',
            'Ag_Mgt':   'Assests/float_img_colors.csv',
            'Land_Mgt': 'Assests/float_img_colors.csv',
            'Non-Ag':   'Assests/float_img_colors.csv'
            }

data_types = {'lumap': 'integer',
                'lmmap': 'integer',
                'ammap': 'integer',
                'non_ag': 'integer',
                'Ag_LU': 'float',
                'Ag_Mgt': 'float',
                'Land_Mgt': 'float',
                'Non-Ag': 'float'
                }

legend_positions = {'lumap': 'bottomright',
                    'lmmap': 'bottomright',
                    'ammap': 'bottomright',
                    'non_ag': 'bottomright',
                    'Ag_LU': 'bottomright',
                    'Ag_Mgt': 'bottomright',
                    'Land_Mgt': 'bottomright',
                    'Non-Ag': 'bottomright'
                    }