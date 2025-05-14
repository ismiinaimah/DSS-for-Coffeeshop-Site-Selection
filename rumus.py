import numpy as np

# --- AHP ---
def calculate_ahp_weights(matrix):
    matrix = np.array(matrix)
    n = matrix.shape[0]

    # Normalisasi kolom
    col_sum = matrix.sum(axis=0)
    norm_matrix = matrix / col_sum

    # Hitung rata-rata baris sebagai bobot
    weights = norm_matrix.mean(axis=1)

    # Konsistensi AHP
    lamda_max = (np.dot(matrix, weights) / weights).mean()
    CI = (lamda_max - n) / (n - 1) if n > 1 else 0
    RI_dict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24,
               7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    RI = RI_dict.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0

    return weights.tolist(), CR

# --- TOPSIS ---
def topsis(matrix, weights, is_benefit):
    matrix = np.array(matrix, dtype=float)
    weights = np.array(weights, dtype=float)

    # Normalisasi Euclidean
    norm = matrix / np.sqrt((matrix**2).sum(axis=0))
    weighted = norm * weights

    # Solusi ideal positif dan negatif
    is_benefit = np.array(is_benefit, dtype=bool)
    ideal_pos = np.where(is_benefit, np.max(weighted, axis=0), np.min(weighted, axis=0))
    ideal_neg = np.where(is_benefit, np.min(weighted, axis=0), np.max(weighted, axis=0))

    # Jarak ke solusi ideal
    d_pos = np.sqrt(((weighted - ideal_pos)**2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_neg)**2).sum(axis=1))

    # Skor preferensi
    scores = d_neg / (d_pos + d_neg)
    ranking = np.argsort(scores)[::-1]  # descending

    return scores.tolist(), ranking.tolist()

# --- PROFILE MATCHING ---
def gap_weight(gap):
    mapping = {
        0: 5.0,
        1: 4.5,
        2: 4.0,
        3: 3.5,
        4: 3.0,
        5: 2.5
    }
    return mapping.get(abs(gap), 1.0)

def profile_matching(ideal, actuals, weights, cf_sf_grouping):
    scores = []

    # Hitung total bobot CF dan SF
    total_cf_weight = sum(w for w, g in zip(weights, cf_sf_grouping) if g == 'CF')
    total_sf_weight = sum(w for w, g in zip(weights, cf_sf_grouping) if g == 'SF')

    for alt in actuals:
        cf_scores = []
        sf_scores = []

        for ideal_val, actual_val, group in zip(ideal, alt, cf_sf_grouping):
            gap = actual_val - ideal_val
            score = gap_weight(gap)

            if group == 'CF':
                cf_scores.append(score)
            else:
                sf_scores.append(score)

        # Rata-rata GAP score per grup
        avg_cf = sum(cf_scores) / len(cf_scores) if cf_scores else 0
        avg_sf = sum(sf_scores) / len(sf_scores) if sf_scores else 0

        final_score = (avg_cf * total_cf_weight) + (avg_sf * total_sf_weight)
        scores.append(final_score)

    ranking = np.argsort(scores)[::-1]
    return scores, ranking.tolist()
