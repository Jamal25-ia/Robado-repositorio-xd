from config import *
import queue_families
import logging

class commandPoolInputChunk:


    def __init__(self):

        self.device = None
        self.physicalDevice = None
        self.surface = None
        self.instance = None

class commandbufferInputChunk:


    def __init__(self):

        self.device = None
        self.commandPool = None
        self.frames = None

def make_command_pool(inputChunk):

    queueFamilyIndices = queue_families.find_queue_families(
        device = inputChunk.physicalDevice,
        instance = inputChunk.instance,
        surface = inputChunk.surface,
    )

    poolInfo = VkCommandPoolCreateInfo(
        queueFamilyIndex=queueFamilyIndices.graphicsFamily,
        flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
    )

    try:
        commandPool = vkCreateCommandPool(
            inputChunk.device, poolInfo, None
        )
        logging.logger.print("Created command pool")
        return commandPool
    except:

        logging.logger.print("Failed to create command pool")
        return None

def make_command_buffers(inputChunk):

    allocInfo = VkCommandBufferAllocateInfo(
        commandPool = inputChunk.commandPool,
        level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        commandBufferCount = 1
    )

    #Make a command buffer for each frame
    for i,frame in enumerate(inputChunk.frames):

        try:
            frame.commandbuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]

            logging.logger.print(f"Allocated command buffer for frame {i}")
        except:
            logging.logger.print(f"Failed to allocate command buffer for frame {i}")
    
    try:
        commandbuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]

        logging.logger.print("Allocated main command buffer")
        
        return commandbuffer
    except:
        logging.logger.print("Failed to allocate main command buffer")
        
        return None