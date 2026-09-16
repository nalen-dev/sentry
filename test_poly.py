def get_path_segments(points):
    segs = []
    total_len = 0
    for i in range(len(points)-1):
        p1 = points[i]
        p2 = points[i+1]
        dist = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
        segs.append({'p1': p1, 'p2': p2, 'len': dist, 'start_l': total_len})
        total_len += dist
    return segs, total_len

def interpolate_poly(points, r1, r2):
    segs, total_len = get_path_segments(points)
    target_start = r1 * total_len
    target_end = r2 * total_len
    
    result_lines = []
    
    for s in segs:
        s_end_l = s['start_l'] + s['len']
        
        # Check if the segment overlaps with [target_start, target_end]
        if s_end_l > target_start and s['start_l'] < target_end:
            # calculate the sub-segment
            local_start = max(target_start, s['start_l']) - s['start_l']
            local_end = min(target_end, s_end_l) - s['start_l']
            
            # ratios on this specific segment
            lr1 = local_start / s['len']
            lr2 = local_end / s['len']
            
            x1 = s['p1'][0] + lr1 * (s['p2'][0] - s['p1'][0])
            y1 = s['p1'][1] + lr1 * (s['p2'][1] - s['p1'][1])
            x2 = s['p1'][0] + lr2 * (s['p2'][0] - s['p1'][0])
            y2 = s['p1'][1] + lr2 * (s['p2'][1] - s['p1'][1])
            
            result_lines.append(((x1, y1), (x2, y2)))
            
    return result_lines

points = [(60,372), (60,314), (130,314), (130,372)]
print(interpolate_poly(points, 0, 0.5))
print(interpolate_poly(points, 0.5, 1.0))

