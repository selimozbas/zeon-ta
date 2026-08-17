# Chaikin Osilatörü

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/chaikin_oscillator.md)

`zeonta.chaikin_oscillator()` — MACD's fast-EMA-minus-slow-EMA shape applied to the A/D Line instead of price.

## Ne ölçer

`macd`'nin fiyata uyguladığı hızlı-EMA eksi yavaş-EMA şeklinin, burada `adl`'ye uygulanmış hâli. ADL'nin kendisi yalnızca alım-satım baskısının kümülatif *seviyesini* söyler; onun iki EMA'sının farkını almak bunu bir değişim hızı okumasına dönüştürür — birikim/dağıtımın şu anda hızlanıp hızlanmadığını gösterir, tıpkı `awesome_oscillator`'ın ham fiyatla kurduğu ilişki gibi.

## Formül

```text
ChaikinOsc = EMA(ADL, hızlı) - EMA(ADL, yavaş)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `3` |
| `slow` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `ADOSC_3_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chaikin_oscillator(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25   -433147.921630
2024-10-26   -548733.439778
2024-10-27   -586042.606100
Name: ADOSC_3_10, dtype: float64
```

**Accessor biçimi:** `df.zta.chaikin_oscillator(...)`

## Nasıl okunur

Sıfır merkezli herhangi bir momentum osilatörü gibi okuyun: sıfırın üzerine çıkması ADL'nin yukarı yönde hızlandığını (alım baskısının kendi yakın ortalamasından daha hızlı arttığını) işaret eder, altına inmesi tersini işaret eder. Chaikin Osilatörü ile fiyat arasındaki bir uyumsuzluk — fiyat yeni bir zirve yaparken osilatörün bunu yapamaması — `macd` uyumsuzluğuyla aynı ayı-uyumsuzluğu mantığıyla okunur.

## Dikkat edilmesi gerekenler

`adl`'nin sahip olduğu her uyarıyı miras alır: çok dar bir yüksek-düşük aralığı, altındaki Para Akışı Çarpanı'nı gürültülü yapar ve bütün yapı doğal bir sıfırlama noktası olmayan bir kümülatif toplam üzerine kuruludur. İki EMA'nın farkı olduğu için `macd`'nin kendi gecikmesini de miras alır — her iki EMA da aynı altta yatan seriye tepki verir, bu yüzden osilatör ADL'nin trendindeki bir değişimi, tam o an değil, gerçekleştikten birkaç bar sonra yansıtır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator)
