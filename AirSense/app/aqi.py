# CPCB-style Indian AQI bands. This compact implementation estimates AQI
# from PM2.5 and PM10 only; official CPCB AQI requires sufficient pollutant
# measurements and pollutant-specific averaging periods.
PM25_BREAKPOINTS = [(0,30,0,50),(31,60,51,100),(61,90,101,200),
                    (91,120,201,300),(121,250,301,400),(251,500,401,500)]
PM10_BREAKPOINTS = [(0,50,0,50),(51,100,51,100),(101,250,101,200),
                    (251,350,201,300),(351,430,301,400),(431,600,401,500)]

def sub_index(value, breakpoints):
    if value is None:
        return None
    for clo, chi, ilo, ihi in breakpoints:
        if clo <= value <= chi:
            return round((ihi-ilo)/(chi-clo)*(value-clo)+ilo)
    if value > breakpoints[-1][1]:
        return 500
    return 0

def estimate_india_aqi(pm25=None, pm10=None):
    values = [x for x in (sub_index(pm25, PM25_BREAKPOINTS),
                          sub_index(pm10, PM10_BREAKPOINTS)) if x is not None]
    return max(values) if values else None

def category(aqi):
    if aqi is None: return ("Unavailable", "No sufficient pollutant data")
    if aqi <= 50: return ("Good", "Minimal impact")
    if aqi <= 100: return ("Satisfactory", "Minor breathing discomfort to sensitive people")
    if aqi <= 200: return ("Moderate", "Breathing discomfort to sensitive people")
    if aqi <= 300: return ("Poor", "Breathing discomfort on prolonged exposure")
    if aqi <= 400: return ("Very Poor", "Respiratory illness on prolonged exposure")
    return ("Severe", "May affect healthy people and seriously impact sensitive groups")
