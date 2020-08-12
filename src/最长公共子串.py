import numpy

def main(str1: str, str2: str):
    m, n = len(str1), len(str2)
    ans = 0
    dp = numpy.zeros((m+1, n+1), dtype=int)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                ans = max(ans, dp[i][j])
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    print(dp)
    return dp[-1][-1]


if __name__ == "__main__":
    print(main("fishi", "hizhii"))
