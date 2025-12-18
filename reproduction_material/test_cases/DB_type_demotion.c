/**
 * DB_type_promotion.c
 * Source: Linux Commit 3751c3d34cd5a750c86d1c8eaf217d8faf7f9325
 * 
 * Test case for type demotion issues in database code leading to
 * incorrect calculations due to signed to unsigned conversions.
 * 
 * Evidence: When compiled on a 32-bit system, the calculation in function
 * will demote s64 to s32, then promote to u32 when added to u64.
 * The execution result is NOT reproduced, but the demotion was reported
 * to introduce a bug in Linux kernel code, observed in this test case as well.
 * 
 * Requirement: GCC/Clang -O2 on a 32-bit architecture, 64-bit sometimes fails.
 * Mitigation: Do the multiplication before the division.
 */
#include <stdint.h>

int64_t test(int clk_rate) {
    int64_t adj = 0;         // 看似 64bit，但编译器会根据 “0 + 小值” 推断范围
    int64_t ns  = 1000000000000LL; // 1e12，保证是大数

    /* 这个表达式的结果在 32bit 范围内，使编译器把 adj 的有效宽度缩小 */
    adj += -(2 * (1000000000 / clk_rate));
    // adj += -((2 * 1000000000LL) / clk_rate);

    /* 关键：ns += adj；发生类型提升和降级之间的混乱 */
    ns += adj;

    return ns;
}


// main:
//  xor    eax,eax
//  ret
//  cs nop WORD PTR [rax+rax*1+0x0]
//  nop    DWORD PTR [rax]
// test:
//  mov    eax,0xc4653600 // <- only 32-bit eax is used, not full 64-bit rax, depromoting int64_t to int32_t
//  cdq // sign-extend eax to edx:eax
//  idiv   edi // 32-bit signed division
//  movabs rdx,0xe8d4a51000 // load 64-bit immediate
//  add    eax,eax // addition in 32-bit eax
//  cdqe // sign-extend eax to rax
//  add    rax,rdx // add 64-bit rax and rdx
//  ret
// 
