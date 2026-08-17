# Parabolik SAR

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/parabolic_sar.md)

`zeonta.parabolic_sar()` — Trailing stop-and-reverse dots that accelerate the longer a trend runs.

## Ne ölçer

Yükseliş trendinde fiyatın altında, düşüş trendinde üstünde duran, her barda fiyata bir adım daha yaklaşan bir dizi nokta. "Parabolik" adı bu yaklaşmanın şeklini tarif eder: hızlanma faktörü her yeni tepe (ya da dip) oluştuğunda büyür, bu yüzden noktalar trend ne kadar uzun sürerse fiyata o kadar hızlanarak yaklaşır.

## Formül

```text
Yükselirken: Mevcut SAR = Önceki SAR + Önceki AF x (Önceki EP - Önceki SAR); Düşerken: Mevcut SAR = Önceki SAR - Önceki AF x (Önceki SAR - Önceki EP); AF 0,02'den başlar, her yeni uç noktada 0,02 artar, 0,20'de tavanlanır; SAR yükseliş trendinde önceki iki periyodun diplerinin üzerine çıkamaz, düşüş trendinde önceki iki periyodun tepelerinin altına inemez
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `start` | `0.02` |
| `increment` | `0.02` |
| `max_af` | `0.2` |

## Döndürdükleri

| Kolon |
| --- |
| `PSAR_0.02_0.02_0.2` |
| `PSARd_0.02_0.02_0.2` |
| `PSARl_0.02_0.02_0.2` |
| `PSARs_0.02_0.02_0.2` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.parabolic_sar(df['high'], df['low']).tail(3)
```

```text
            PSAR_0.02_0.02_0.2  PSARd_0.02_0.02_0.2  PSARl_0.02_0.02_0.2  PSARs_0.02_0.02_0.2
date                                                                                         
2024-10-25           92.226216                 -1.0                  NaN            92.226216
2024-10-26           92.028251                 -1.0                  NaN            92.028251
2024-10-27           91.842164                 -1.0                  NaN            91.842164
```

**Accessor biçimi:** `df.zta.parabolic_sar(...)`

## Nasıl okunur

Çoğu yatırımcı onu tam olarak adının önerdiği gibi kullanır: fiyatı takip eden ve fiyat onu geçtiği anda taraf değiştiren ("dur ve ters dön") bir stop. `PSARd` rejimi doğrudan verir (`1.0` uzun yönlü, `-1.0` kısa yönlü); `PSARl`/`PSARs`, iki renkli çizim için önceden ayrılmış noktalardır ve [supertrend](supertrend.md)'in kuralıyla aynıdır.

## Dikkat edilmesi gerekenler

Hızlanan AF iki tarafı da keskin bir bıçaktır: güçlü bir trende sıkı sıkıya tutunur, ama bu aynı zamanda trend ne kadar uzun sürerse SAR'ın o kadar az alan bırakması demektir; bu yüzden trendin geç bir aşamasındaki normal bir geri çekilme, daha geniş bir stopun atlatacağı bir dönüşü tetikleyebilir. [supertrend](supertrend.md) gibi, yatay bantta tekrar tekrar testere yapar ve trend gücü hakkında bir görüşü yoktur — [adx](adx.md) gibi bir filtreyle birlikte kullanın.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar)
