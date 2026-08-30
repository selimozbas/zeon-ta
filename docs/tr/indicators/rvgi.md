# Göreceli Canlılık Endeksi (RVGI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/rvgi.md)

`zeonta.rvgi()` — Symmetrically weighted ratio of body strength to range: a smoother BOP.

## Ne ölçer

[bop](bop.md)'un ham olarak ölçtüğü aynı fikir — barın kendi aralığına göre kapanış gücü — aynı anda iki şekilde yumuşatılır: her birinin SMA'sından önce hem gövde hem aralık üzerinde 4-barlık simetrik bir ağırlıklandırma, artı kendi sinyal çizgisi için tekrar aynı ağırlıklandırma.

## Formül

```text
Gövde/Aralık her biri 4 bar üzerinden simetrik ağırlıklandırılır (1-2-2-1), sonra RVGI = SMA(Gövde, n) / SMA(Aralık, n)
```

## Parametreler

**Gerekli girdiler:** `open`, `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `RVGI_10` |
| `RVGIs_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.rvgi(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
             RVGI_10  RVGIs_10
date                          
2024-10-25 -0.069802 -0.082001
2024-10-26 -0.113195 -0.082534
2024-10-27 -0.181959 -0.103652
```

**Accessor biçimi:** `df.zta.rvgi(...)`

## Nasıl okunur

RVGI ile kendi sinyal çizgisi arasındaki kesişim standart okumadır — ham BOP'un kendi sıfır çizgisini kesmesini izlemenin daha pürüzsüz, daha az çalkantılı bir versiyonu.

## Dikkat edilmesi gerekenler

Sıfır-aralıklı ya da sıfır-gövdeli barlar, SMA yumuşatmasının kendisinin ötesinde özel olarak korunmaz — uzun bir özdeş açılış/kapanış ya da yüksek/düşük bar dizisi yine de tanımsız bir `0/0` oranı üretebilir, bu da `NaN` olarak ortaya çıkar.

## Kaynak

Formül kaynağı: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index)
