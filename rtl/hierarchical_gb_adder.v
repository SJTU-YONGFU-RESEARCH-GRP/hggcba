`timescale 1ns / 1ps

module hierarchical_gb_adder #(
    parameter integer DATA_WIDTH = 16,
    parameter integer BLOCK_SIZE = 4
) (
    input  wire [DATA_WIDTH-1:0] a,
    input  wire [DATA_WIDTH-1:0] b,
    input  wire                  cin,
    output wire [DATA_WIDTH-1:0] sum,
    output wire                  cout
);
    localparam integer NUM_BLOCKS = (DATA_WIDTH + BLOCK_SIZE - 1) / BLOCK_SIZE;

    wire [NUM_BLOCKS:0] carry_block;
    assign carry_block[0] = cin;

    genvar bi;
    generate
        for (bi = 0; bi < NUM_BLOCKS; bi = bi + 1) begin : g_blocks
            localparam integer START = bi * BLOCK_SIZE;
            localparam integer END = (((bi + 1) * BLOCK_SIZE) < DATA_WIDTH) ? ((bi + 1) * BLOCK_SIZE) : DATA_WIDTH;
            localparam integer BW = END - START;

            wire [BW-1:0] a_slice;
            wire [BW-1:0] b_slice;
            wire [BW-1:0] p_bits;
            wire [BW-1:0] g_bits;
            wire [BW:0] carry_local;
            wire [BW:0] gprefix;
            wire block_propagate;
            wire block_generate;
            wire selected_carry;

            assign a_slice = a[END-1:START];
            assign b_slice = b[END-1:START];
            assign p_bits = a_slice ^ b_slice;
            assign g_bits = a_slice & b_slice;
            assign block_propagate = &p_bits;
            assign carry_local[0] = carry_block[bi];
            assign gprefix[0] = 1'b0;

            genvar j;
            for (j = 0; j < BW; j = j + 1) begin : g_local
                assign sum[START + j] = p_bits[j] ^ carry_local[j];
                assign carry_local[j + 1] = g_bits[j] | (p_bits[j] & carry_local[j]);
                assign gprefix[j + 1] = g_bits[j] | (p_bits[j] & gprefix[j]);
            end

            assign block_generate = gprefix[BW];
            assign selected_carry = block_generate | (block_propagate & carry_block[bi]);
            assign carry_block[bi + 1] = selected_carry;
        end
    endgenerate

    assign cout = carry_block[NUM_BLOCKS];
endmodule
