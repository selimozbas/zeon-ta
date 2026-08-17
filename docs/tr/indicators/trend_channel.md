# Trend Temelleri ve Trend Kanalları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/trend_channel.md)

`zeonta.trend_channel()` — Linear-regression trend line with standard-deviation channel bands.

## Ne ölçer

"Bu bir yükseliş trendi mi?" sorusu genelde göz kararı yanıtlanır. En küçük kareler uyumu bunu bir sayıyla yanıtlar: eğim. Uyumun etrafındaki kanal bantları da fiyatın trende ne kadar sıkı yapıştığını gösterir.

## Formül

```text
n bar uzunluğunda doğrusal regresyon (x = 0..n-1, y = kapanış): eğim b = (nSxy - SxSy) / (nSx^2 - (Sx)^2); kesişim a = (Sy - bSx) / n; regresyon çizgisi = a + b*x. Kanal bantları = regresyon çizgisi +/- (çarpan x kapanışların regresyon çizgisinden standart sapması).
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `100` |
| `multiplier` | `2.0` |

## Döndürdükleri

| Kolon |
| --- |
| `LRCM_100` |
| `LRCU_100` |
| `LRCL_100` |
| `LRCSLOPE_100` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trend_channel(df['close'], length=50).tail(3)
```

```text
              LRCM_50    LRCU_50    LRCL_50  LRCSLOPE_50
date                                                    
2024-10-25  90.207156  91.314703  89.099609    -0.054643
2024-10-26  90.072080  91.214641  88.929520    -0.057086
2024-10-27  89.891669  91.106883  88.676454    -0.060957
```

**Accessor biçimi:** `df.zta.trend_channel(...)`

## Nasıl okunur

`LRCSLOPE` bar başına düşen sürüklenmedir: pozitifse yükseliş, negatifse düşüş trendi; büyüklüğü ise trendin dikliğidir. `LRCU`'ya yakın fiyat trende göre gerilmiştir; `LRCL`'ye yakın fiyat ise trendin gerisinde kalmıştır. Bant genişliği fiyatın ortalamadan değil, **uyum çizgisinden** sapmasıdır; bu yüzden temiz bir trendde kanal, trend ne kadar dik olursa olsun dar kalır.

## Dikkat edilmesi gerekenler

Uyum her barda yeniden hesaplanır, dolayısıyla yeni veri geldikçe kanal yeniden çizilir — bugün geçmiş barların üzerinde gördüğünüz çizgi, o zaman var olan çizgi değildir. Ayrıca regresyon, saf gürültünün içinden de gönül rahatlığıyla bir doğru geçirir; eğime güvenmeden önce ADX gibi bir ölçüyle karşılaştırın.
