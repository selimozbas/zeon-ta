# Arnaud Legoux Hareketli Ortalaması (ALMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/alma.md)

`zeonta.alma()` — Gaussian-weighted moving average tuned by an offset (lag vs. smoothness) and sigma.

## Ne ölçer

[wma](wma.md) pencereyi doğrusal, [ema](ema.md) ise üssel olarak ağırlıklandırırken, ALMA onu, tepe konumu (`offset`) ve genişliği (`sigma`) ayrı ayrı ayarlanabilen bir Gauss çan eğrisiyle ağırlıklandırır — her hareketli ortalamanın yaptığı aynı gecikme-karşı-pürüzsüzlük ödünleşimi için iki bağımsız düğme.

## Formül

```text
m = taban(offset*(n-1)); s = n/sigma; w[j] = exp(-(j-m)^2/(2*s^2)), j=0..n-1; ALMA = toplam(w[j] * Kapanış[t-n+1+j]) / toplam(w[j])
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `9` |
| `offset` | `0.85` |
| `sigma` | `6.0` |

## Döndürdükleri

| Kolon |
| --- |
| `ALMA_9_0.85_6.0` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.alma(df['close']).tail(3)
```

```text
date
2024-10-25    90.160843
2024-10-26    90.147718
2024-10-27    89.829007
Name: ALMA_9_0.85_6.0, dtype: float64
```

**Accessor biçimi:** `df.zta.alma(...)`

## Nasıl okunur

Herhangi bir hareketli ortalama gibi okunur. `1`'e yakın bir `offset`, daha duyarlı bir EMA gibi davranır; `0`'a yakın bir `offset` ise daha pürüzsüz, merkezlenmiş bir ortalama gibi davranır — `0,85`, bir orta nokta değil, duyarlılığa doğru ayarlanmış bir başlangıç noktasıdır.

## Dikkat edilmesi gerekenler

Sonucu anlamlı şekilde değiştiren, `length`'in ötesinde iki ek parametre (`offset`, `sigma`) — varsayılanları evrensel sabitler değil, Legoux'nun kendi başlangıç noktası olarak ele alın; bu kütüphanenin Ehlers'in kendi ayarlanabilir filtrelerine verdiği aynı uyarı.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/](https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/)
