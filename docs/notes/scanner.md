---
id: vevdbc23ddsqjpqdb6guvzr
title: Scanner
desc: ''
updated: 1681299665718
created: 1681299655824
---

## Matching Reserved Words and Idenfifiers

Our scanner is almost done. The only remaining pieces of the lexical grammar to implement are identifiers and their close cousins, the reserved words. You might think we could match keywords like or in the same way we handle multiple-character operators like <=.

```
case 'o':
if (match('r')) {
addToken(OR);
}
break;
```

Consider what would happen if a user named a variable orchid. The scanner would see the first two letters, or, and immediately emit an or keyword token. This gets us to an important principle called maximal munch. When two lexical grammar rules can both match a chunk of code that the scanner is looking at, _whichever one matches the most characters wins._

That rule states that if we can match orchid as an identifier and or as a keyword, then the former wins. This is also why we tacitly assumed, previously, that <= should be scanned as a single <= token and not < followed by =.

Maximal munch means we can’t easily detect a reserved word until we’ve reached the end of what might instead be an identifier. After all, a reserved word is an identifier, it’s just one that has been claimed by the language for its own use. That’s where the term **reserved word** comes from.
