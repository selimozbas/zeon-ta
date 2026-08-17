# Ultimate Osilatör

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ultimate_oscillator.md)

`zeonta.ultimate_oscillator()` — Larry Williams' three-timeframe blend of buying pressure over true range.

## Ne ölçer

Larry Williams tarafından, tek periyotlu osilatörlerin yanlış uyumsuzluk sinyali verme eğilimini düzeltmek için özel olarak geliştirildi: üç farklı geriye bakışı (en hızlıya doğru 4:2:1 ağırlıklı) tek bir çizgide harmanlayarak, yalnızca kısa pencerede ayı gibi görünen bir uyumsuzluk, iki uzun pencere aynı fikirde olmadığında geçersiz kılınır. Alım Baskısı (BP) ve Gerçek Aralık (TR), geçerli barın kendi açılışına değil *önceki* kapanışa göre ölçülür; böylece bir boşluk (gap), o barın aralığına görünmez kalmak yerine aralığın bir parçası sayılır.

## Formül

```text
AB = Kapanış - Min(Düşük, ÖncekiKapanış); GA = Max(Yüksek, ÖncekiKapanış) - Min(Düşük, ÖncekiKapanış); Ortalama_n = Toplam(AB, n) / Toplam(GA, n); UO = 100 x (4xOrtalama_hızlı + 2xOrtalama_orta + Ortalama_yavaş) / 7
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `7` |
| `medium` | `14` |
| `slow` | `28` |

## Döndürdükleri

| Kolon |
| --- |
| `UO_7_14_28` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ultimate_oscillator(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    43.163796
2024-10-26    42.451754
2024-10-27    41.226164
Name: UO_7_14_28, dtype: float64
```

**Accessor biçimi:** `df.zta.ultimate_oscillator(...)`

## Nasıl okunur

70'in üzerindeki okumalar aşırı alım, 30'un altındakiler aşırı satım kabul edilir — Williams'ın kendisinin tarif ettiği klasik alım sinyali, boğa uyumsuzluğunun (fiyat daha düşük bir dip yaparken UO yapmaması) ardından 50'nin üzerine geri kırılmasıdır; tek başına herhangi biri değil, üç koşulun birlikte gerçekleşmesidir.

## Dikkat edilmesi gerekenler

Üç pencere `hızlı < orta < yavaş` koşulunu sağlamalıdır; sırasız verilmesi sessizce anlamsız bir şey hesaplamak yerine `ValueError` fırlatır. RSI ve Stokastik gibi, aşırı alım ya da aşırı satım okumasında olmak tek başına bir işlem sinyali değildir — Williams'ın kendi kuralı, tek başına ham seviyeyi değil, uyumsuzluk-artı-50-kırılımı kombinasyonunu gerektirir.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator)
