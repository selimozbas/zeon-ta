# Negatif Hacim Endeksi (NVI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/nvi.md)

`zeonta.nvi()` — Cumulative index that only moves on a bar where volume fell versus the prior bar.

## Ne ölçer

Paul Dysart'ın 1930'lar-40'lardan kalma, Norman Fosback tarafından popülerleştirilen fikri: fiyatın *sakin* (düşen) hacim günlerindeki hareketleri, bir kalabalık çekmeden hareket eden bilgili paranın yansıması olma ihtimali daha yüksektir, ağır hacim günlerindeki hareketler ise kalabalık güdümlü etkinliği yansıtır. NVI yalnızca sakin günlerde güncellenir, her ağır-hacim barında düz kalır — [pvi](pvi.md)'nin aynanın-tersi tamamlayıcısıdır.

## Formül

```text
1000'den başlar. Hacim[i] < Hacim[i-1] olduğunda: NVI[i] = NVI[i-1] * (1 + (Kapanış[i]-Kapanış[i-1])/Kapanış[i-1]); aksi halde değişmez
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `NVI` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.nvi(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    1093.934042
2024-10-26    1082.069032
2024-10-27    1074.337105
Name: NVI, dtype: float64
```

**Accessor biçimi:** `df.zta.nvi(...)`

## Nasıl okunur

StockCharts'ın kendi uzun vadeli çalışması, NVI kendi 255-günlük hareketli ortalamasının üstünde otururken piyasanın altında oturmasına göre daha sık boğa piyasasında olduğunu buldu — kısa vadeli bir sinyal yerine uzun vadeli, düşük frekanslı bir rejim okuması olarak kullanılır.

## Dikkat edilmesi gerekenler

Başlangıç değeri olan `1000`, formülün bir yasası değil bir gelenektir (StockCharts'ın) — bazı diğer uygulamalar `100` ya da `1`'den başlar. Bir NVI serisini yalnızca kendisiyle karşılaştırın (kendi hareketli ortalaması ya da kendi geçmişi), asla mutlak seviyesini farklı bir sembolünkiyle karşılaştırmayın.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi)
