# VWAP (Hacim Ağırlıklı Ortalama Fiyat)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vwap.md)

`zeonta.vwap()` — Volume-weighted average price with standard-deviation bands.

## Ne ölçer

Bugün fiilen ödenen ortalama fiyatın, her seviyede ne kadar işlem gördüğüne göre ağırlıklandırılmış hâli. Bir grafik çalışmasından çok bir kıyas ölçütüdür: kurumlar VWAP'a göre değerlendirilir; fiyatın ona doğru çekilmesinin sebebi de budur.

## Formül

```text
Tipik Fiyat = (Yüksek + Düşük + Kapanış) / 3; VWAP = toplam(Tipik Fiyat x Hacim) / toplam(Hacim), her seans açılışında sıfırlanır; Üst/Alt Bant = VWAP +/- k x stdev(hacme göre ağırlıklandırılmış Tipik Fiyat)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `anchor` | `'session'` |
| `length` | `20` |
| `std` | `1.0` |

## Döndürdükleri

| Kolon |
| --- |
| `VWAP_session` |
| `VWAPU_session` |
| `VWAPL_session` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwap(df['high'], df['low'], df['close'], df['volume'], anchor='rolling', length=20).tail(3)
```

```text
            VWAP_rolling_20  VWAPU_rolling_20  VWAPL_rolling_20
date                                                           
2024-10-25        90.640999         91.326784         89.955215
2024-10-26        90.599117         91.327749         89.870484
2024-10-27        90.528552         91.327042         89.730063
```

**Accessor biçimi:** `df.zta.vwap(...)`

## Nasıl okunur

VWAP'ın üstündeki fiyat, alıcıların seans ortalamasına kıyasla fazla ödediği anlamına gelir. Bantlar seans içindeki istatistiksel olarak gerilmiş seviyeleri işaretler. Gerçek bir açılışı olan enstrümanlarda `anchor="session"`, kripto gibi 7/24 açık piyasalarda `anchor="rolling"` kullanın.

## Dikkat edilmesi gerekenler

Hiç sıfırlanmayan bir VWAP tamamen farklı bir istatistiktir ve kıyas ölçütü anlamını yitirir — sıfırlama işin özüdür. Seans çıpası, seans sınırlarını bulmak için bir `DatetimeIndex` gerektirir; olmadığında bu fonksiyon sessizce yanlış bir şey hesaplamak yerine hata yükseltir.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/vwap](https://ta.cognicode.org/learn/vwap)
