//! Agregasi sampel ~12 detik menjadi baris riwayat per menit per segmen.

use std::collections::HashMap;

use chrono::{DateTime, TimeZone, Utc};
use dts_shared::{HistoryRow, SegmentKey};

struct Acc {
    sum: f64,
    n: u32,
    min: f32,
    max: f32,
}

#[derive(Default)]
pub struct Aggregator {
    minute: Option<i64>,
    acc: HashMap<SegmentKey, Acc>,
}

/// (segmen, temp_avg, temp_min, temp_max)
pub type Sample = (SegmentKey, f32, f32, f32);

impl Aggregator {
    /// Tambahkan satu snapshot. Jika menit berganti, kembalikan baris menit sebelumnya.
    pub fn add(&mut self, now: DateTime<Utc>, samples: &[Sample]) -> Option<Vec<HistoryRow>> {
        let m = now.timestamp() - now.timestamp().rem_euclid(60);
        let mut flushed = None;
        match self.minute {
            Some(cur) if cur != m => {
                flushed = Some(self.drain(cur));
                self.minute = Some(m);
            }
            None => self.minute = Some(m),
            _ => {}
        }
        for (key, avg, min, max) in samples {
            let a = self.acc.entry(*key).or_insert(Acc { sum: 0.0, n: 0, min: *min, max: *max });
            a.sum += f64::from(*avg);
            a.n += 1;
            a.min = a.min.min(*min);
            a.max = a.max.max(*max);
        }
        flushed
    }

    fn drain(&mut self, minute: i64) -> Vec<HistoryRow> {
        let ts = Utc.timestamp_opt(minute, 0).single().unwrap_or_else(Utc::now);
        self.acc
            .drain()
            .map(|(key, a)| HistoryRow {
                key,
                ts,
                temp_avg: (a.sum / f64::from(a.n)) as f32,
                temp_min: a.min,
                temp_max: a.max,
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn at(secs: i64) -> DateTime<Utc> {
        Utc.timestamp_opt(1_800_000_000 + secs, 0).unwrap()
    }

    #[test]
    fn flush_saat_menit_berganti() {
        let k = SegmentKey { dts_ch: 1, dts_code: 1 };
        let mut agg = Aggregator::default();
        let base = 1_800_000_000 % 60; // detik ke dalam menit untuk titik awal
        let t0 = -(base);
        assert!(agg.add(at(t0 + 1), &[(k, 30.0, 29.0, 31.0)]).is_none());
        assert!(agg.add(at(t0 + 13), &[(k, 40.0, 28.0, 45.0)]).is_none());
        let rows = agg.add(at(t0 + 61), &[(k, 50.0, 50.0, 50.0)]).expect("harus flush");
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].temp_avg, 35.0);
        assert_eq!(rows[0].temp_min, 28.0);
        assert_eq!(rows[0].temp_max, 45.0);
        assert_eq!(rows[0].ts.timestamp() % 60, 0);
    }
}
