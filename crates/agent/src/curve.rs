//! Parsing kolom `curvebuff.str`: nilai dipisah koma, satuan 0,1 C, indeks = jarak (meter).

use dts_shared::LivePointSample;

/// Nilai mentah <= -2000 (mis. -2731 = -273,1 C) berarti tidak ada sensor.
const NO_SENSOR_RAW: f32 = -2000.0;

/// Ambil titik pada rentang [start, end] (inklusif), dengan end dibatasi panjang data.
pub fn parse_curve(ch: i32, raw: &str, start: usize, end: usize) -> Vec<LivePointSample> {
    let vals: Vec<&str> = raw.split(',').collect();
    if vals.is_empty() {
        return vec![];
    }
    let end = end.min(vals.len() - 1);
    let start = start.min(end);
    (start..=end)
        .map(|i| {
            let temp = vals[i]
                .trim()
                .parse::<f32>()
                .ok()
                .filter(|v| *v > NO_SENSOR_RAW)
                .map(|v| v / 10.0);
            LivePointSample { dts_ch: ch, dts_code: i as i32, temp }
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn konversi_dan_rentang() {
        let p = parse_curve(4, "400,401,-2731,abc,500", 1, 3);
        assert_eq!(p.len(), 3);
        assert_eq!(p[0].dts_code, 1);
        assert_eq!(p[0].temp, Some(40.1));
        assert_eq!(p[1].temp, None); // -2731 = tidak ada sensor
        assert_eq!(p[2].temp, None); // tidak bisa di-parse
    }

    #[test]
    fn end_dibatasi_panjang_data() {
        let p = parse_curve(1, "100,200", 0, 99);
        assert_eq!(p.len(), 2);
    }
}
