# Heikin-Ashi Mumları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/heikin_ashi.md)

`zeonta.heikin_ashi()` — Recursively smoothed candles that filter noise from the price bars themselves.

## Ne ölçer

'Ortalama bar' — gerçek OHLC serisinden ikinci, düzleştirilmiş bir seri oluşturur; burada her barın açılışı, *önceki* barın kendi düzleştirilmiş açılış ve kapanışını içine katar. [ema](ema.md)'nın tek bir fiyat çizgisine uyguladığı aynı türden özyinelemeli, kendine-referans veren düzleştirme, burada tüm bir muma uygulanır.

## Formül

```text
HAclose=(O+H+L+C)/4; HAopen[0]=(O+C)/2 sonra (HAopen[-1]+HAclose[-1])/2; HAhigh=max(H,HAopen,HAclose); HAlow=min(L,HAopen,HAclose)
```

## Parametreler

**Gerekli girdiler:** `open`, `high`, `low`, `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `HAopen` |
| `HAhigh` |
| `HAlow` |
| `HAclose` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.heikin_ashi(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
               HAopen     HAhigh    HAlow   HAclose
date                                               
2024-10-25  90.360474  90.827100  89.7648  90.29595
2024-10-26  90.328212  90.328212  89.0960  89.66890
2024-10-27  89.998556  89.998556  88.0724  88.85595
```

**Accessor biçimi:** `df.zta.heikin_ashi(...)`

## Nasıl okunur

Az ya da hiç ters-renkli fitili olmayan aynı-yönlü bir mum dizisi, henüz gerçek dönüş baskısı göstermemiş bir trend için klasik okumadır — düz bir mum grafiğinin hâlâ bar bar göstereceği gürültü burada filtrelenmiştir.

## Dikkat edilmesi gerekenler

Özyinelemeli açılış, tek bir eksik barın o noktadan sonraki her Heikin-Ashi değerini değiştirdiği anlamına gelir — bu kütüphanedeki çoğu indikatörden farklı olarak, etkinin içinden çıkıp gideceği sabit bir pencere yoktur.

## Kaynak

Formül kaynağı: [https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi](https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi)
