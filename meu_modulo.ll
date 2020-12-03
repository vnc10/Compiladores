; ModuleID = "meu_modulo.bc"
target triple = "unknown-unknown-unknown"
target datalayout = ""

@"a" = common global i32 0, align 4
define i32 @"principal"() 
{
entryprincipal:
  %"ret" = alloca i32, align 4
se:
  %".2" = load i32, i32* @"a"
  %".3" = load i32, i32* @"a"
  %"compara" = icmp ugt i32 %".2", %".3"
  br i1 %"compara", label %"então", label %"senão"
"então":
"senão":
  br label %"volta"
volta:
se.1:
  %".5" = load i32, i32* @"a"
  %".6" = load i32, i32* @"a"
  %"compara.1" = icmp ult i32 %".5", %".6"
  br i1 %"compara.1", label %"então.1", label %"senão.1"
"então.1":
  br label %"volta.1"
"senão.1":
  br label %"volta.1"
volta.1:
  br label %"volta"
se.2:
  %".12" = load i32, i32* @"a"
  %".13" = load i32, i32* @"a"
  %"compara.2" = icmp ult i32 %".12", %".13"
  br i1 %"compara.2", label %"então.2", label %"senão.2"
"então.2":
  br label %"volta.2"
"senão.2":
  br label %"volta.2"
volta.2:
exitprincipal:
}
