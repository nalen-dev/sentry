//! Level alarm per segmen dengan deadband, identik dengan logika di Dashboard.tsx
//! (supaya status di cloud sama dengan yang dilihat operator di desktop).

use dts_shared::SegmentStatus;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Level {
    #[default]
    Normal,
    Warning,
    Critical,
}

impl Level {
    pub fn to_i32(self) -> i32 {
        match self {
            Level::Normal => 0,
            Level::Warning => 1,
            Level::Critical => 2,
        }
    }
    pub fn from_i32(v: i32) -> Self {
        match v {
            1 => Level::Warning,
            2 => Level::Critical,
            _ => Level::Normal,
        }
    }
}

impl From<Level> for SegmentStatus {
    fn from(l: Level) -> Self {
        match l {
            Level::Normal => SegmentStatus::Normal,
            Level::Warning => SegmentStatus::Warning,
            Level::Critical => SegmentStatus::Critical,
        }
    }
}

/// Deadband 0,5 C agar status tidak bolak-balik di sekitar threshold.
pub fn next_level(prev: Level, temp: f32, warning: f32, critical: f32) -> Level {
    if temp >= critical {
        Level::Critical
    } else if temp >= warning && (prev != Level::Critical || temp > warning + 0.5) {
        Level::Warning
    } else if temp < warning - 0.5 {
        Level::Normal
    } else {
        prev
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const W: f32 = 60.0;
    const C: f32 = 70.0;

    #[test]
    fn konversi_i32_bolak_balik() {
        for l in [Level::Normal, Level::Warning, Level::Critical] {
            assert_eq!(Level::from_i32(l.to_i32()), l);
        }
    }

    #[test]
    fn naik_ke_warning_dan_critical() {
        assert_eq!(next_level(Level::Normal, 59.9, W, C), Level::Normal);
        assert_eq!(next_level(Level::Normal, 60.0, W, C), Level::Warning);
        assert_eq!(next_level(Level::Warning, 70.0, W, C), Level::Critical);
    }

    #[test]
    fn deadband_menahan_status() {
        // Dari Warning, turun sedikit di bawah batas: tetap Warning (di dalam deadband).
        assert_eq!(next_level(Level::Warning, 59.7, W, C), Level::Warning);
        // Di bawah batas - 0,5: kembali Normal.
        assert_eq!(next_level(Level::Warning, 59.4, W, C), Level::Normal);
        // Dari Critical, turun ke area 60..60,5: tetap Critical.
        assert_eq!(next_level(Level::Critical, 60.3, W, C), Level::Critical);
        // Dari Critical, turun ke > 60,5: Warning.
        assert_eq!(next_level(Level::Critical, 60.6, W, C), Level::Warning);
    }
}
