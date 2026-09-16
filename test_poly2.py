import math

def getPathSegments(points):
    segs = []
    totalLen = 0
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        dist = math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))
        segs.append({"p1": p1, "p2": p2, "len": dist, "startL": totalLen})
        totalLen += dist
    return {"segs": segs, "totalLen": totalLen}

def interpolatePoly(points, r1, r2):
    res = getPathSegments(points)
    segs = res["segs"]
    totalLen = res["totalLen"]
    targetStart = r1 * totalLen
    targetEnd = r2 * totalLen
    
    lines = []
    
    for s in segs:
        sEndL = s["startL"] + s["len"]
        if sEndL > targetStart and s["startL"] < targetEnd:
            localStart = max(targetStart, s["startL"]) - s["startL"]
            localEnd = min(targetEnd, sEndL) - s["startL"]
            
            lr1 = localStart / s["len"]
            lr2 = localEnd / s["len"]
            
            x1 = s["p1"][0] + lr1 * (s["p2"][0] - s["p1"][0])
            y1 = s["p1"][1] + lr1 * (s["p2"][1] - s["p1"][1])
            x2 = s["p1"][0] + lr2 * (s["p2"][0] - s["p1"][0])
            y2 = s["p1"][1] + lr2 * (s["p2"][1] - s["p1"][1])
            
            lines.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
            
    return lines

points = [[513, 360], [513, 314], [410, 314], [410, 372]]
lines = interpolatePoly(points, 0, 0.5)
for l in lines:
    print(l)

