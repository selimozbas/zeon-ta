# Ulcer Endeksi

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ulcer_index.md)

`zeonta.ulcer_index()` — Drawdown-based risk measure — the expected percentage decline, not price swing size.

## Ne ölçer

Hareketi *her iki yönde* de ölçen `atr` ya da `bbands`'ın aksine, Ulcer Endeksi (Peter Martin, 1987) yalnızca fiyatın kendi yakın zirvesinden ne kadar düştüğünü ölçer — geri çekilmeyi ortalamadan önce karesini almak, tek bir derin düşüşün, aynı toplam büyüklükteki birkaç küçük düşüşten çok daha fazla okumaya hakim olması anlamına gelir; bu, gerçek bir geri çekilmeyi elde tutmanın gerçekte nasıl hissettirdiğini yansıtır.

## Formül

```text
YüzdeGeriÇekilme = (Kapanış - EnYüksekKapanış(n)) / EnYüksekKapanış(n) x 100; UI = sqrt(ortalama(YüzdeGeriÇekilme^2, n))
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `UI_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ulcer_index(df['close']).tail(3)
```

```text
date
2024-10-25    1.909861
2024-10-26    2.083540
2024-10-27    2.327038
Name: UI_14, dtype: float64
```

**Accessor biçimi:** `df.zta.ulcer_index(...)`

## Nasıl okunur

Daha yüksek okumalar, daha derin ve daha sürdürülen geri çekilmeler anlamına gelir — riskten kaçınan bir yatırımcının, ham fiyat dalgalanmaları (`atr` ile ölçüldüğünde) özellikle büyük olmasa bile katlanmakta zorlanacağı bir menkul kıymet. Aday yatırımlar arasında Ulcer Endeksi'ni karşılaştırmak, ortalama getirilerinden bağımsız olarak tarihsel olarak ne kadar geri çekilme acısına neden olduklarına göre sıralamanın bir yoludur.

## Dikkat edilmesi gerekenler

Aslında yatırım fonları düşünülerek tasarlandı ve yalnızca aşağı yönlü riske odaklanır — yukarı yönlü potansiyel hakkında hiçbir şey söylemez, bu yüzden bir getiri ölçütünün yerine değil, onu tamamlayıcı olarak kullanılmalıdır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index)
