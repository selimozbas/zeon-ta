# Stokastik RSI (StochRSI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/stoch_rsi.md)

`zeonta.stoch_rsi()` — The Stochastic formula applied to RSI instead of price — momentum of momentum.

## Ne ölçer

`stoch`'un aralık-konumu formülünü aynen alıp fiyat yerine `rsi`'a uygular — bir osilatörün osilatörü. RSI tek başına momentumu ölçer; StochRSI ise o momentum okumasının kendi son dönem tarihine göre ne kadar uç olduğunu ölçer; bu da onun RSI'nin kendisinden çok daha sık ve çok daha keskin biçimde sınırları arasında salınmasına yol açar.

## Formül

```text
StochRSI = (RSI - EnDüşükDip(RSI, n)) / (EnYüksekZirve(RSI, n) - EnDüşükDip(RSI, n))
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `rsi_length` | `14` |
| `stoch_length` | `14` |
| `smooth_k` | `3` |
| `smooth_d` | `3` |

## Döndürdükleri

| Kolon |
| --- |
| `STOCHRSIk_14_14_3_3` |
| `STOCHRSId_14_14_3_3` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stoch_rsi(df['close']).tail(3)
```

```text
            STOCHRSIk_14_14_3_3  STOCHRSId_14_14_3_3
date                                                
2024-10-25            42.204660            34.814315
2024-10-26            25.801741            34.817172
2024-10-27            10.968497            26.324966
```

**Accessor biçimi:** `df.zta.stoch_rsi(...)`

## Nasıl okunur

80'in üstü geleneksel olarak "aşırı alım", 20'nin altı "aşırı satım" sayılır — ama StochRSI, RSI'den çok daha oynak olduğu için bu uç noktalara yakın çok daha fazla zaman geçirir; bu yüzden 50 çizgisinin kesilmesini ya da %K'nin %D'yi kesmesini tek başına uç değerlerden daha kullanışlı sinyaller olarak değerlendirin.

## Dikkat edilmesi gerekenler

RSI'nin kendisi yatay hâle geldiğinde — en belirgin biçimde güçlü bir trend boyunca 100'e ya da 0'a yapıştığında — StochRSI'nin kendi yüksek-düşük aralığı sıfıra çöker ve gösterge bir uçta kalmak yerine orta noktaya (50) döner; bu da olmayan bir dönüş sinyali gibi görünebilir. Ayrıca iki kez türetilmiş bir göstergedir (fiyatın RSI'si, sonra RSI'nin Stokastiği), bu yüzden tekil okumalara gerçek bir temkinle yaklaşın.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi)
