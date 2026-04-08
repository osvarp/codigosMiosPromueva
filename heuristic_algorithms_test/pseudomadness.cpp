#include "gen.cpp"
// taken from yosupo's submission on https://judge.yosupo.jp/submission/49544
// the answer seems to be the characteristic polynomial of the sequence

template <class T> std::vector<T> berlekamp_massey(const std::vector<T>& s) {
    int n = int(s.size());
    std::vector<T> b = {T(-1)}, c = {T(-1)};
    T y = T(1);
    for (int ed = 1; ed <= n; ed++) {
        int l = int(c.size()), m = int(b.size());
        T x = 0;
        for (int i = 0; i < l; i++) {
            x += c[i] * s[ed - l + i];
        }
        b.push_back(0);
        m++;
        if (x == T(0)) continue;
        T freq = x / y;
        if (l < m) {
            // use b
            auto tmp = c;
            c.insert(begin(c), m - l, T(0));
            for (int i = 0; i < m; i++) {
                c[m - 1 - i] -= freq * b[m - 1 - i];
            }
            b = tmp;
            y = x;
        } else {
            // use c
            for (int i = 0; i < m; i++) {
                c[l - 1 - i] -= freq * b[m - 1 - i];
            }
        }
    }
    return c;
}