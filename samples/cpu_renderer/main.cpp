#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cmath>
#include <numbers>
#include <vector>
#include <string_view>
#include <chrono>
#include <thread>

// https://github.com/richgel999/fpng
#include "fpng.h"

int32_t main(int32_t argc, const char* argv[]) {
    // レンダラー起動時間を取得。
    using clock = std::chrono::high_resolution_clock;
    const clock::time_point appStartTp = clock::now();

    uint32_t timeLimit = UINT32_MAX;
    for (int argIdx = 1; argIdx < argc; ++argIdx) {
        std::string_view arg = argv[argIdx];
        if (arg == "--time-limit") {
            if (argIdx + 1 >= argc) {
                printf("missing value.\n");
                return -1;
            }
            timeLimit = static_cast<uint32_t>(atoi(argv[argIdx + 1]));
            argIdx += 1;
        }
        else {
            printf("Unknown argument %s.\n", argv[argIdx]);
            return -1;
        }
    }



    using namespace fpng;
    fpng_init();

    struct RGBA {
        uint32_t r : 8;
        uint32_t g : 8;
        uint32_t b : 8;
        uint32_t a : 8;
    };
    constexpr uint32_t width = 256;
    constexpr uint32_t height = 256;
    std::vector<RGBA> pixels(height * width);

    for (uint32_t frameIndex = 0; frameIndex < 600; ++frameIndex) {
        const clock::time_point frameStartTp = clock::now();
        printf("Frame %u ... ", frameIndex);

        // 高度なレンダリング...
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                RGBA v;
                v.r = x;
                v.g = y;
                v.b = 127 + 127 * std::sinf(2 * std::numbers::pi_v<float> * (frameIndex % 60) / 60.0f);
                v.a = 255;
                const int32_t idx = y * width + x;
                pixels[idx] = v;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));

        // 起動からの時刻とフレーム時間を計算。
        const clock::time_point now = clock::now();
        const clock::duration frameTime = now - frameStartTp;
        const clock::duration totalTime = now - appStartTp;
        if (std::chrono::duration_cast<std::chrono::milliseconds>(totalTime).count() > 1e+3f * timeLimit)
            break;
        printf(
            "Done: %.3f [ms] (total: %.3f [s])\n",
            std::chrono::duration_cast<std::chrono::microseconds>(frameTime).count() * 1e-3f,
            std::chrono::duration_cast<std::chrono::milliseconds>(totalTime).count() * 1e-3f);

        // 3桁連番で画像出力。
        char filename[256];
        sprintf_s(filename, "%03u.png", frameIndex);
        fpng_encode_image_to_file(filename, pixels.data(), width, height, 4, 0);
    }

    return 0;
}
