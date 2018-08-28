#!/usr/local/bin/lua

--??????????????:
t =
{
    [1] = {A = 5, B = 2},
    [2] = {A = 1, B = 3},
    [3] = {A = 3, B = 6},
    [4] = {A = 7, B = 1},
    [5] = {A = 2, B = 9},
}

table.sort(t, function(a, b) return a.A > b.A; end)
for k, v in pairs(t) do
    print(k)
    for key, value in pairs(v) do
        print(key, value)
    end
end


--table ??????, ?????? == ???
--??????????? v==a[i] ??????????? equal(v,a[i]):
function removeRepeated(a)
    for k, v in pairs(a) do
        local count = 0
        for j in pairs(a) do
            count = count + 1
        end
        for i=k+1, count do
            if v==a[i] then
                table.remove(a, i)
            end
        end
    end
end
local a = {"a", "d", "c", "g", "d", "w", "c", "a", "g", "s"}
removeRepeated(a)
for k, v in pairs(a) do
    print(k, v)
end