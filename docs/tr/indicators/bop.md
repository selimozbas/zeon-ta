# Güç Dengesi (BOP)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/bop.md)

`zeonta.bop()` — Where the close landed between open and the bar's range, unweighted by volume.

## Ne ölçer

Igor Livshin'in 2001'deki, barı kimin doğrudan kazandığının ölçüsü: alıcılar kapanışı açılıştan yukarı mı itti (pozitif), yoksa satıcılar aşağı mı itti (negatif) — barın kendi aralığının genişliğine göre ölçeklenmiş. [cmf](cmf.md)'nin Para Akışı Çarpanına benzer şekle sahiptir, ama hacimle ağırlıklandırmak yerine açılıştan ölçülür ve bir pencere üzerinden toplanmak yerine ham bar-başı oran olarak bırakılır.

## Formül

```text
BOP = (Kapanış - Açılış) / (Yüksek - Düşük)
```

## Parametreler

**Gerekli girdiler:** `open`, `high`, `low`, `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `BOP` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bop(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25   -0.376071
2024-10-26   -0.959853
2024-10-27   -0.476996
Name: BOP, dtype: float64
```

**Accessor biçimi:** `df.zta.bop(...)`

## Nasıl okunur

Ham değerler bardan bara çalkantılıdır; birçok yatırımcı daha düzgün bir çizgi için bunu kendisi `sma()`'ya besler — StockCharts'ın kendi sayfasının sunduğu biçim de budur; bu fonksiyon, TA-Lib'in kendi parametresiz geleneğine uymak için yumuşatılmamış oranı döndürür.

## Dikkat edilmesi gerekenler

Sıfır-aralıklı barlar (`Yüksek == Düşük`) sıfıra bölüm yaratır; hata fırlatmak ya da uyarı üretmek yerine `0` olarak ele alınır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop)
