`timescale 1ns / 1ps

module tb_hierarchical_gb_adder;
    localparam integer DATA_WIDTH = 16;
    localparam integer BLOCK_SIZE = 4;
    localparam integer RANDOM_TESTS = 500;

    reg  [DATA_WIDTH-1:0] a;
    reg  [DATA_WIDTH-1:0] b;
    reg                   cin;
    wire [DATA_WIDTH-1:0] sum;
    wire                  cout;
    reg  [DATA_WIDTH:0]   expected;
    integer               i;
    integer               errors;
    integer               seed;

    hierarchical_gb_adder #(
        .DATA_WIDTH(DATA_WIDTH),
        .BLOCK_SIZE(BLOCK_SIZE)
    ) dut (
        .a(a),
        .b(b),
        .cin(cin),
        .sum(sum),
        .cout(cout)
    );

    task check_case;
        begin
            #1;
            expected = a + b + cin;
            if ({cout, sum} !== expected) begin
                errors = errors + 1;
                $display(
                    "Mismatch a=%h b=%h cin=%0d got={%0d,%h} exp=%h",
                    a, b, cin, cout, sum, expected
                );
            end
        end
    endtask

    initial begin
        errors = 0;
        seed = 32'h20260422;

        a = 0; b = 0; cin = 0; check_case();
        a = 0; b = 0; cin = 1; check_case();
        a = {DATA_WIDTH{1'b1}}; b = 1; cin = 0; check_case();
        a = {DATA_WIDTH{1'b1}}; b = {DATA_WIDTH{1'b1}}; cin = 1; check_case();
        a = 16'hAAAA; b = 16'h5555; cin = 0; check_case();

        for (i = 0; i < RANDOM_TESTS; i = i + 1) begin
            a = $random(seed);
            b = $random(seed);
            cin = $random(seed) & 1'b1;
            check_case();
        end

        if (errors == 0) begin
            $display("TB_PASS tests=%0d", RANDOM_TESTS + 5);
        end else begin
            $display("TB_FAIL errors=%0d", errors);
            $fatal(1);
        end
        $finish;
    end
endmodule
